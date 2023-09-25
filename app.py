"""
Created By:    Cristian Scutaru
Creation Date: Sep 2023
Company:       XtractPro Software
"""

import configparser, re, json, os
import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session


class Theme:
    def __init__(self, color, fillcolor, fillcolorC,
            bgcolor, icolor, tcolor, style, shape, pencolor, penwidth):
        self.color = color
        self.fillcolor = fillcolor
        self.fillcolorC = fillcolorC
        self.bgcolor = bgcolor
        self.icolor = icolor
        self.tcolor = tcolor
        self.style = style
        self.shape = shape
        self.pencolor = pencolor
        self.penwidth = penwidth


class Table:
    def __init__(self, name, comment):
        self.name = name
        self.comment = comment if comment is not None and comment != 'None' else ''
        self.label = None

        self.columns = []           # list of all columns
        self.uniques = {}           # dictionary with UNIQUE constraints, by name + list of columns
        self.pks = []               # list of PK columns (if any)
        self.fks = {}               # dictionary with FK constraints, by name + list of FK columns


    @classmethod
    def getClassName(cls, name, useUpperCase, withQuotes=True):
        if re.match("^[A-Z_0-9]*$", name) == None:
            return f'"{name}"' if withQuotes else name
        return name.upper() if useUpperCase else name.lower()


    def getName(self, useUpperCase, withQuotes=True):
        return Table.getClassName(self.name, useUpperCase, withQuotes)


    def getColumn(self, name):
        for column in self.columns:
            if column.name == name:
                return column
        return None


    def getUniques(self, name, useUpperCase):
        constraint = self.uniques[name]
        uniques = [column.getName(useUpperCase) for column in constraint]
        ulist = ", ".join(uniques)

        if useUpperCase:
            return (f',\n  CONSTRAINT {Table.getClassName(name, useUpperCase)}\n'
                + f"    UNIQUE ({ulist})")
        return (f',\n  constraint {Table.getClassName(name, useUpperCase)}\n'
            + f"    unique ({ulist})")


    def getPKs(self, useUpperCase):
        pks = [column.getName(useUpperCase) for column in self.pks]
        pklist = ", ".join(pks)
        pkconstraint = self.pks[0].pkconstraint

        if useUpperCase:
            return (f',\n  CONSTRAINT {Table.getClassName(pkconstraint, useUpperCase)}\n'
                + f"    PRIMARY KEY ({pklist})")
        return (f',\n  constraint {Table.getClassName(pkconstraint, useUpperCase)}\n'
            + f"    primary key ({pklist})")


    def getFKs(self, name, useUpperCase):
        constraint = self.fks[name]
        pktable = constraint[0].fkof.table

        fks = [column.getName(useUpperCase) for column in constraint]
        fklist = ", ".join(fks)
        pks = [column.fkof.getName(useUpperCase) for column in constraint]
        pklist = ", ".join(pks)

        if useUpperCase:
            return (f"ALTER TABLE {self.getName(useUpperCase)}\n"
                + f"  ADD CONSTRAINT {Table.getClassName(name, useUpperCase)}\n"
                + f"  ADD FOREIGN KEY ({fklist})\n"
                + f"  REFERENCES {pktable.getName(useUpperCase)} ({pklist});\n\n")
        return (f"alter table {self.getName(useUpperCase)}\n"
            + f"  add constraint {Table.getClassName(name, useUpperCase)}\n"
            + f"  add foreign key ({fklist})\n"
            + f"  references {pktable.getName(useUpperCase)} ({pklist});\n\n")


    # outputs a CREATE TABLE statement for the current table
    def getCreateTable(self, useUpperCase):
        if useUpperCase:
            s = f"CREATE OR REPLACE TABLE {self.getName(useUpperCase)} ("
        else:
            s = f"create or replace table {self.getName(useUpperCase)} ("
        
        first = True
        for column in self.columns:
            if first: first = False
            else: s += ","
            s += column.getCreateColumn(useUpperCase)

        if len(self.uniques) > 0:
            for constraint in self.uniques:
                s += self.getUniques(constraint, useUpperCase)
        if len(self.pks) >= 1:
            s += self.getPKs(useUpperCase)
        
        s += "\n)"
        if self.comment != '':
            comment = self.comment.replace("'", "''")
            s += f" comment = '{comment}'" if not useUpperCase else f" COMMENT = '{comment}'"
        return s + ";\n\n"


    def getDotShape(self, theme, showColumns, showTypes, useUpperCase):
        fillcolor = theme.fillcolorC if showColumns else theme.fillcolor
        colspan = "2" if showTypes else "1"
        tableName = self.getName(useUpperCase, False)
        s = (f'  {self.label} [\n'
            + f'    fillcolor="{fillcolor}" color="{theme.color}" penwidth="1"\n'
            + f'    label=<<table style="{theme.style}" border="0" cellborder="0" cellspacing="0" cellpadding="1">\n'
            + f'      <tr><td bgcolor="{theme.bgcolor}" align="center"'
            + f' colspan="{colspan}"><font color="{theme.tcolor}"><b>{tableName}</b></font></td></tr>\n')

        if showColumns:
            for column in self.columns:
                name = column.getName(useUpperCase, False)
                if column.ispk: name = f"<u>{name}</u>"
                if column.fkof != None: name = f"<i>{name}</i>"
                if column.nullable: name = f"{name}*"
                if column.identity: name = f"{name} I"
                if column.isunique: name = f"{name} U"
                datatype = column.datatype
                if useUpperCase: datatype = datatype.upper()

                if showTypes:
                    s += (f'      <tr><td align="left"><font color="{theme.icolor}">{name}&nbsp;</font></td>\n'
                        + f'        <td align="left"><font color="{theme.icolor}">{datatype}</font></td></tr>\n')
                else:
                    s += f'      <tr><td align="left"><font color="{theme.icolor}">{name}</font></td></tr>\n'

        return s + '    </table>>\n  ]\n'


    def getDotLinks(self, theme):
        s = ""
        for constraint in self.fks:
            fks = self.fks[constraint]
            fk1 = fks[0]
            dashed = "" if not fk1.nullable else ' style="dashed"'
            arrow = "" if fk1.ispk and len(self.pks) == len(fk1.fkof.table.pks) else ' arrowtail="crow"'
            s += (f'  {self.label} -> {fk1.fkof.table.label}'
                + f' [ penwidth="{theme.penwidth}" color="{theme.pencolor}"{dashed}{arrow} ]\n')
        return s


class Column:
    def __init__(self, table, name, comment):
        self.table = table
        self.name = name
        self.comment = comment if comment is not None and comment != 'None' else ''
        self.nullable = True
        self.datatype = None        # with (length, or precision/scale)
        self.identity = False

        self.isunique = False
        self.ispk = False
        self.pkconstraint = None
        self.fkof = None            # points to the PK column on the other side


    def getName(self, useUpperCase, withQuotes=True):
        return Table.getClassName(self.name, useUpperCase, withQuotes)


    def setDataType(self, datatype):
        self.datatype = datatype["type"]
        self.nullable = bool(datatype["nullable"])

        if self.datatype == "FIXED":
            self.datatype = "NUMBER"
        elif "fixed" in datatype:
            fixed = bool(datatype["fixed"])
            if self.datatype == "TEXT":
                self.datatype = "CHAR" if fixed else "VARCHAR"

        if "length" in datatype:
            self.datatype += f"({str(datatype['length'])})"
        elif "scale" in datatype:
            if int(datatype['precision']) == 0:
                self.datatype += f"({str(datatype['scale'])})"
                if self.datatype == "TIMESTAMP_NTZ(9)":
                    self.datatype = "TIMESTAMP"
            elif "scale" in datatype and int(datatype['scale']) == 0:
                self.datatype += f"({str(datatype['precision'])})"
                if self.datatype == "NUMBER(38)":
                    self.datatype = "INT"
                elif self.datatype.startswith("NUMBER("):
                    self.datatype = f"INT({str(datatype['precision'])})"
            elif "scale" in datatype:
                self.datatype += f"({str(datatype['precision'])},{str(datatype['scale'])})"
                #if column.datatype.startswith("NUMBER("):
                #    column.datatype = f"FLOAT({str(datatype['precision'])},{str(datatype['scale'])})"
        self.datatype = self.datatype.lower()


    # outputs the column definition in a CREATE TABLE statement, for the parent table
    def getCreateColumn(self, useUpperCase):
        nullable = "" if self.nullable or (self.ispk and len(self.table.pks) == 1) else " not null"
        if useUpperCase: nullable = nullable.upper()
        identity = "" if not self.identity else " identity"
        if useUpperCase: identity = identity.upper()
        pk = ""     # if not self.ispk or len(self.table.pks) >= 2 else " primary key"
        if useUpperCase: pk = pk.upper()
        datatype = self.datatype
        if useUpperCase: datatype = datatype.upper()
        
        comment = self.comment.replace("'", "''")
        if comment != '': comment = f" COMMENT '{comment}'" if useUpperCase else f" comment '{comment}'"

        return f"\n  {self.getName(useUpperCase)} {datatype}{nullable}{identity}{pk}{comment}"


# @st.cache_resource(show_spinner="Reading metadata...")
def importMetadata(database, schema):
    global session
    tables = {}
    if database == '' or schema == '': return tables
    suffix = f"in schema {Table.getClassName(database, False)}.{Table.getClassName(schema, False)}"

    # get tables
    query = f"show tables {suffix}"
    results = session.sql(query).collect()
    for row in results:
        tableName = str(row["name"])
        table = Table(tableName, str(row["comment"]))
        tables[tableName] = table
        table.label = f"n{len(tables)}"

    # get table columns
    query = f"show columns {suffix}"
    results = session.sql(query).collect()
    for row in results:
        tableName = str(row["table_name"])
        if tableName in tables:
            table = tables[tableName]

            name = str(row["column_name"])
            column = Column(table, name, str(row["comment"]))
            table.columns.append(column)

            column.identity = str(row["autoincrement"]) != ''
            column.setDataType(json.loads(str(row["data_type"])))

    # get UNIQUE constraints
    query = f"show unique keys {suffix}"
    results = session.sql(query).collect()
    for row in results:
        tableName = str(row["table_name"])
        if tableName in tables:
            table = tables[tableName]
            column = table.getColumn(str(row["column_name"]))

            # add a UNIQUE constraint (if not there) with the current column
            constraint = str(row["constraint_name"])
            if constraint not in table.uniques:
                table.uniques[constraint] = []
            table.uniques[constraint].append(column)
            column.isunique = True

    # get PKs
    query = f"show primary keys {suffix}"
    results = session.sql(query).collect()
    for row in results:
        tableName = str(row["table_name"])
        if tableName in tables:
            table = tables[tableName]
            column = table.getColumn(str(row["column_name"]))
            column.ispk = True
            column.pkconstraint = str(row["constraint_name"])

            pos = int(row["key_sequence"]) - 1
            table.pks.insert(pos, column)

    # get FKs
    query = f"show imported keys {suffix}"
    results = session.sql(query).collect()
    for row in results:
        pktableName = str(row["pk_table_name"])
        fktableName = str(row["fk_table_name"])
        if pktableName in tables and fktableName in tables:
            pktable = tables[pktableName]
            pkcolumn = pktable.getColumn(str(row["pk_column_name"]))
            fktable = tables[fktableName]
            fkcolumn = fktable.getColumn(str(row["fk_column_name"]))

            # add a constraint (if not there) with the current FK column
            if str(row["pk_schema_name"]) == str(row["fk_schema_name"]):
                constraint = str(row["fk_name"])
                if constraint not in fktable.fks:
                    fktable.fks[constraint] = []
                fktable.fks[constraint].append(fkcolumn)

                fkcolumn.fkof = pkcolumn
                #print(f"{fktable.name}.{fkcolumn.name} -> {pktable.name}.{pkcolumn.name}")
    
    return tables


def createScript(tables, database, schema, useUpperCase):
    db = Table.getClassName(database, useUpperCase)
    sch = f'{db}.{Table.getClassName(schema, useUpperCase)}'
    if useUpperCase: s = f"USE DATABASE {db};\nCREATE OR REPLACE SCHEMA {sch};\n\n"
    else: s = f"use database {db};\ncreate or replace schema {sch};\n\n"

    for name in tables:
        s += tables[name].getCreateTable(useUpperCase)
    for name in tables:
        for constraint in tables[name].fks:
            s += tables[name].getFKs(constraint, useUpperCase)
    return s


def createGraph(tables, theme, showColumns, showTypes, useUpperCase):
    s = ('digraph {\n'
        + '  graph [ rankdir="LR" bgcolor="#ffffff" ]\n'
        + f'  node [ style="filled" shape="{theme.shape}" gradientangle="180" ]\n'
        + '  edge [ arrowhead="none" arrowtail="none" dir="both" ]\n\n')

    for name in tables:
        s += tables[name].getDotShape(theme, showColumns, showTypes, useUpperCase)
    s += "\n"
    for name in tables:
        s += tables[name].getDotLinks(theme)
    s += "}\n"
    return s


def getSession():
    try:
        return get_active_session()
    except:
        parser = configparser.ConfigParser()
        parser.read(os.path.join(os.path.expanduser('~'), ".snowsql/config"))
        section = "connections.my_conn"
        pars = {
            "account": parser.get(section, "accountname"),
            "user": parser.get(section, "username"),
            "password": parser.get(section, "password")
        }
        return Session.builder.configs(pars).create()


def getThemes():
    return {
        "Common Gray": Theme("#6c6c6c", "#e0e0e0", "#f5f5f5",
            "#e0e0e0", "#000000", "#000000", "rounded", "Mrecord", "#696969", "1"),
        "Blue Navy": Theme("#1a5282", "#1a5282", "#ffffff",
            "#1a5282", "#000000", "#ffffff", "rounded", "Mrecord", "#0078d7", "2"),
        #"Gradient Green": Theme("#716f64", "#008080:#ffffff", "#008080:#ffffff",
        #    "transparent", "#000000", "#000000", "rounded", "Mrecord", "#696969", "1"),
        #"Blue Sky": Theme("#716f64", "#d3dcef:#ffffff", "#d3dcef:#ffffff",
        #    "transparent", "#000000", "#000000", "rounded", "Mrecord", "#696969", "1"),
        "Common Gray Box": Theme("#6c6c6c", "#e0e0e0", "#f5f5f5",
            "#e0e0e0", "#000000", "#000000", "rounded", "record", "#696969", "1")
    }

def getDatabase():
    global session
    names = []
    query = "show databases"
    results = session.sql(query).collect()
    for row in results:
        names.append(str(row["name"]))
    sel = 0 if "Chinook" not in names else names.index("Chinook")
    return st.sidebar.selectbox('Database', tuple(names), index=sel,
        help="Select an existing database")


def getSchema(database):
    global session
    names = []
    if database != "":
        query = f"show schemas in database {Table.getClassName(database, False)}"
        results = session.sql(query).collect()
        for row in results:
            schemaName = str(row["name"])
            if schemaName != "INFORMATION_SCHEMA":
                names.append(schemaName)
    sel = 0 if "PUBLIC" not in names else names.index("PUBLIC")
    return st.sidebar.selectbox('Schema', tuple(names), index=sel, 
        help="Select a schema for the current database")

st.set_page_config(layout="wide")
session = getSession()
themes = getThemes()
database = getDatabase()
schema = getSchema(database)

st.sidebar.divider()
theme = st.sidebar.selectbox('Theme', tuple(themes.keys()), index=0, 
    help="Select another color theme")
showColumns = st.sidebar.checkbox('Display Column Names', value=False, 
    help="Show columns in the expanded table shapes")
showTypes = st.sidebar.checkbox('Display Data Types', value=False, 
    help="Show column data type names when the table shapes are expanded")
useUpperCase = st.sidebar.checkbox('Use Upper Case', value=False, 
    help="Use upper case for table, column, and data type names, and for the script keywords")

with st.spinner('Reading metadata...'):
    tables = importMetadata(database, schema)
if database == '' or schema == '':
    st.write("Select a database and a schema.")
elif len(tables) == 0:
    st.write("Found no tables in the current database and schema.")
else:
    with st.spinner('Generating diagram and script...'):
        graph = createGraph(tables, themes[theme], showColumns, showTypes, useUpperCase)
        script = createScript(tables, database, schema, useUpperCase)

        tabERD, tabDOT, tabScript = st.tabs(["ERD Viewer", "DOT Code", "Create Script"])
        tabERD.graphviz_chart(graph, use_container_width=True)
        tabDOT.code(graph, language="dot", line_numbers=True)
        tabScript.code(script, language="sql", line_numbers=True)
