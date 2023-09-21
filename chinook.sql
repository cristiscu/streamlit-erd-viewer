-- Created By:    Cristian Scutaru
-- Creation Date: Sep 2023
-- Company:       XtractPro Software

CREATE OR REPLACE DATABASE "Chinook";

CREATE TABLE "Album" (
    "Album ID" INT NOT NULL AUTOINCREMENT,
    "Title" VARCHAR(160) NOT NULL comment 'Title of the Album',
    "Artist ID" INT NOT NULL,
    CONSTRAINT "PK_Album" PRIMARY KEY  ("Album ID")
) comment = 'Albums created by artists';

CREATE TABLE "Artist" (
    "Artist ID" INT NOT NULL AUTOINCREMENT,
    "Name" VARCHAR(120) comment 'Full name of the artist',
    CONSTRAINT "PK_Artist" PRIMARY KEY  ("Artist ID")
) comment = 'An artist can have one or more albums';

CREATE TABLE "Customer" (
    "Customer ID" INT NOT NULL,
    "First Name" VARCHAR(40) NOT NULL,
    "Last Name" VARCHAR(20) NOT NULL,
    "Company" VARCHAR(80),
    "Address" VARCHAR(70),
    "City" VARCHAR(40),
    "State" VARCHAR(40),
    "Country" VARCHAR(40),
    "Postal Code" VARCHAR(10),
    "Phone" VARCHAR(24),
    "Fax" VARCHAR(24),
    "Email" VARCHAR(60) NOT NULL,
    "Support Rep ID" INT,
    CONSTRAINT "UQ_Name" UNIQUE ("First Name", "Last Name"),
    CONSTRAINT "PK_Customer" PRIMARY KEY  ("Customer ID")
);

CREATE TABLE "Employee" (
    "Employee ID" INT NOT NULL,
    "First Name" VARCHAR(20) NOT NULL,
    "Last Name" VARCHAR(20) NOT NULL,
    "Title" VARCHAR(30),
    "Reports To" INT,
    "Birth Date" DATE,
    "Hire Date" DATE,
    "Address" VARCHAR(70),
    "City" VARCHAR(40),
    "State" VARCHAR(40),
    "Country" VARCHAR(40),
    "Postal Code" VARCHAR(10),
    "Phone" VARCHAR(24),
    "Fax" VARCHAR(24),
    "Email" VARCHAR(60),
    CONSTRAINT "UQ_Name" UNIQUE ("First Name", "Last Name"),
    CONSTRAINT "PK_Employee" PRIMARY KEY  ("Employee ID")
);

CREATE TABLE "Genre" (
    "Genre ID" INT NOT NULL,
    "Name" VARCHAR(120),
    CONSTRAINT "PK_Genre" PRIMARY KEY  ("Genre ID")
);

CREATE TABLE "Invoice" (
    "Invoice ID" INT NOT NULL,
    "Customer ID" INT NOT NULL,
    "Invoice Date" TIMESTAMP NOT NULL,
    "Billing Address" VARCHAR(70),
    "Billing City" VARCHAR(40),
    "Billing State" VARCHAR(40),
    "Billing Country" VARCHAR(40),
    "Billing Postal Code" VARCHAR(10),
    "Total" NUMERIC(10,2) NOT NULL,
    CONSTRAINT "PK_Invoice" PRIMARY KEY  ("Invoice ID")
);

CREATE TABLE "Invoice Line" (
    "Invoice Line ID" INT NOT NULL,
    "Invoice ID" INT NOT NULL,
    "Track ID" INT NOT NULL,
    "Unit Price" NUMERIC(10,2) NOT NULL,
    "Quantity" INT NOT NULL,
    CONSTRAINT "PK_InvoiceLine" PRIMARY KEY  ("Invoice Line ID")
);

CREATE TABLE "Media Type" (
    "Media Type ID" INT NOT NULL,
    "Name" VARCHAR(120),
    CONSTRAINT "PK_MediaType" PRIMARY KEY  ("Media Type ID")
);

CREATE TABLE "Playlist" (
    "Playlist ID" INT NOT NULL,
    "Name" VARCHAR(120),
    CONSTRAINT "PK_Playlist" PRIMARY KEY  ("Playlist ID")
);

CREATE TABLE "Playlist Track" (
    "Playlist ID" INT NOT NULL,
    "Track ID" INT NOT NULL,
    CONSTRAINT "PK_PlaylistTrack" PRIMARY KEY  ("Playlist ID", "Track ID")
);

CREATE TABLE "Track" (
    "Track ID" INT NOT NULL,
    "Name" VARCHAR(200) NOT NULL,
    "Album ID" INT,
    "Media Type ID" INT NOT NULL,
    "Genre ID" INT,
    "Composer" VARCHAR(220),
    "Milliseconds" INT NOT NULL,
    "Bytes" INT,
    "Unit Price" NUMERIC(10,2) NOT NULL,
    CONSTRAINT "PK_Track" PRIMARY KEY  ("Track ID")
);

ALTER TABLE "Album" ADD CONSTRAINT "FK_AlbumArtistId"
    FOREIGN KEY ("Artist ID") REFERENCES "Artist" ("Artist ID");

ALTER TABLE "Customer" ADD CONSTRAINT "FK_CustomerSupportRepId"
    FOREIGN KEY ("Support Rep ID") REFERENCES "Employee" ("Employee ID");

ALTER TABLE "Employee" ADD CONSTRAINT "FK_EmployeeReportsTo"
    FOREIGN KEY ("Reports To") REFERENCES "Employee" ("Employee ID");

ALTER TABLE "Invoice" ADD CONSTRAINT "FK_InvoiceCustomerId"
    FOREIGN KEY ("Customer ID") REFERENCES "Customer" ("Customer ID");

ALTER TABLE "Invoice Line" ADD CONSTRAINT "FK_InvoiceLineInvoiceId"
    FOREIGN KEY ("Invoice ID") REFERENCES "Invoice" ("Invoice ID");

ALTER TABLE "Invoice Line" ADD CONSTRAINT "FK_InvoiceLineTrackId"
    FOREIGN KEY ("Track ID") REFERENCES "Track" ("Track ID");

ALTER TABLE "Playlist Track" ADD CONSTRAINT "FK_PlaylistTrackPlaylistId"
    FOREIGN KEY ("Playlist ID") REFERENCES "Playlist" ("Playlist ID");

ALTER TABLE "Playlist Track" ADD CONSTRAINT "FK_PlaylistTrackTrackId"
    FOREIGN KEY ("Track ID") REFERENCES "Track" ("Track ID");

ALTER TABLE "Track" ADD CONSTRAINT "FK_TrackAlbumId"
    FOREIGN KEY ("Album ID") REFERENCES "Album" ("Album ID");

ALTER TABLE "Track" ADD CONSTRAINT "FK_TrackGenreId"
    FOREIGN KEY ("Genre ID") REFERENCES "Genre" ("Genre ID");

ALTER TABLE "Track" ADD CONSTRAINT "FK_TrackMediaTypeId"
    FOREIGN KEY ("Media Type ID") REFERENCES "Media Type" ("Media Type ID");