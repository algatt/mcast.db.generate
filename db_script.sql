CREATE TABLE Account (
	AccountID UNIQUEIDENTIFIER PRIMARY KEY,
    Email NVARCHAR(255) UNIQUE NOT NULL,
    DateRegistered DATETIME NOT NULL
);

CREATE TABLE Country (
 	CountryID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    Country NVARCHAR(255) NOT NULL UNIQUE
)

CREATE TABLE City (
	CityID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    City NVARCHAR(255) NOT NULL,
    CountryID UNIQUEIDENTIFIER NOT NULL
    FOREIGN KEY(CountryID) REFERENCES Country(CountryID),
    UNIQUE(City, CountryID)
);

CREATE TABLE Profile (
	ProfileID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    DateOfBirth DATE,
    Prefix NVARCHAR(255) NULL,
    FirstName NVARCHAR(255) NOT NULL,
    LastName NVARCHAR(255) NOT NULL,
	StreetAddress NVARCHAR(255) NOT NULL,
    PostCode NVARCHAR(255) NULL,
	CityID UNIQUEIDENTIFIER NOT NULL,
	AccountID UNIQUEIDENTIFIER NOT NULL UNIQUE,
	FOREIGN KEY (AccountID) REFERENCES Account(AccountID),
	FOREIGN KEY (CityID) REFERENCES City(CityID)
); 

CREATE TABLE Brand (
	BrandID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    Brand NVARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE Category (
	CategoryID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    Category NVARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE Product (
	ProductID UNIQUEIDENTIFIER PRIMARY KEY,
    Barcode NVARCHAR(255) UNIQUE,
    Name NVARCHAR(255) NOT NULL,
    BrandID UNIQUEIDENTIFIER NOT NULL,
    CategoryID UNIQUEIDENTIFIER NOT NULL,
    Weight INT NOT NULL,
    Price FLOAT NOT NULL,
    FOREIGN KEY (BrandID) REFERENCES Brand(BrandID),
    FOREIGN KEY (CategoryID) REFERENCES Category(CategoryID)
);

CREATE TABLE Rating (
    RatingID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    ProductID UNIQUEIDENTIFIER NOT NULL,
    Overall FLOAT,
    OneStar INT,
    TwoStar INT,
    ThreeStar INT,
    FourStar INT,
    FiveStar INT,
    ReviewsNumber INT,
    ProductQuality NVARCHAR(50),
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID)
);

CREATE TABLE Orders (
	OrderID UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    AccountID UNIQUEIDENTIFIER NOT NULL,
    OrderDate DATETIME NOT NULL,
    FOREIGN KEY (AccountID) REFERENCES Account(AccountID)
);

CREATE TABLE OrderItem (
	OrderID UNIQUEIDENTIFIER NOT NULL,
    ProductID UNIQUEIDENTIFIER NOT NULL,
    Quantity INT NOT NULL,
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (ProductID) REFERENCES Product(ProductID),
    PRIMARY KEY(OrderId, ProductId)
); 