--create database dml_computer
go
use dml_computer
GO
PRINT N'Recreating the objects for the database'
--Drop all FKs in the database
declare @table_name sysname, @constraint_name sysname
declare i cursor static for 
select c.table_name, a.constraint_name
from INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS a join INFORMATION_SCHEMA.KEY_COLUMN_USAGE b
on a.unique_constraint_name=b.constraint_name join INFORMATION_SCHEMA.KEY_COLUMN_USAGE c
on a.constraint_name=c.constraint_name
WHERE upper(c.table_name) in (upper('Laptop'),'PC',upper('Product'),upper('Printer'))
open i
fetch next from i into @table_name,@constraint_name
while @@fetch_status=0
begin
	exec('ALTER TABLE '+@table_name+' DROP CONSTRAINT '+@constraint_name)
	fetch next from i into @table_name,@constraint_name
end
close i
deallocate i
GO
--Drop all tables
declare @object_name sysname, @sql varchar(8000)
declare i cursor static for 
SELECT table_name from INFORMATION_SCHEMA.TABLES
where upper(table_name) in (upper('Laptop'),'PC',upper('Product'),upper('Printer'))

open i
fetch next from i into @object_name
while @@fetch_status=0
begin
	set @sql='DROP TABLE [dbo].['+@object_name+']'
	exec(@sql)
	fetch next from i into @object_name
end
close i
deallocate i
GO

CREATE TABLE [dbo].[Laptop] (
	[code] [int] NOT NULL ,
	[model] [varchar] (4) NOT NULL ,
	[speed] [smallint] NOT NULL ,
	[ram] [smallint] NOT NULL DEFAULT ((64)),
	[hd] [real] NOT NULL DEFAULT ((20)),
	[price] [money] NULL ,
	[screen] [tinyint] NOT NULL DEFAULT ((14))
) ON [PRIMARY]
GO

CREATE TABLE [dbo].[PC] (
	[code] [int] NOT NULL ,
	[model] [varchar] (4) NOT NULL ,
	[speed] [smallint] NOT NULL ,
	[ram] [smallint] NOT NULL DEFAULT ((128)),
	[hd] [real] NOT NULL DEFAULT ((40)),
	[cd] [varchar] (10) NOT NULL DEFAULT ('40x'),
	[price] [money] NULL 
) ON [PRIMARY]
GO

CREATE TABLE [dbo].[Product] (
	[maker] [char] (1) NOT NULL ,
	[model] [varchar] (4) NOT NULL ,
	[type] [varchar] (7) NOT NULL 
) ON [PRIMARY]
GO

CREATE TABLE [dbo].[Printer] (
	[code] [int] NOT NULL ,
	[model] [varchar] (4) NOT NULL ,
	[color] [char] (1) NOT NULL DEFAULT ('y'),
	[type] [varchar] (6) NOT NULL DEFAULT ('Jet'),
	[price] [money] NULL 
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[Laptop] WITH NOCHECK ADD 
	CONSTRAINT [PK_Laptop] PRIMARY KEY  NONCLUSTERED 
	(
		[code]
	)  ON [PRIMARY] 
GO

ALTER TABLE [dbo].[PC] WITH NOCHECK ADD 
	CONSTRAINT [PK_pc] PRIMARY KEY  NONCLUSTERED 
	(
		[code]
	)  ON [PRIMARY] 
GO

ALTER TABLE [dbo].[Product] WITH NOCHECK ADD 
	CONSTRAINT [PK_product] PRIMARY KEY  NONCLUSTERED 
	(
		[model]
	)  ON [PRIMARY] 
GO

ALTER TABLE [dbo].[Printer] WITH NOCHECK ADD 
	CONSTRAINT [PK_printer] PRIMARY KEY  NONCLUSTERED 
	(
		[code]
	)  ON [PRIMARY] 
GO

ALTER TABLE [dbo].[Laptop] ADD 
	CONSTRAINT [FK_Laptop_product] FOREIGN KEY 
	(
		[model]
	) REFERENCES [dbo].[Product] (
		[model]
	)
GO

ALTER TABLE [dbo].[PC] ADD 
	CONSTRAINT [FK_pc_product] FOREIGN KEY 
	(
		[model]
	) REFERENCES [dbo].[Product] (
		[model]
	)
GO

ALTER TABLE [dbo].[Printer] ADD 
	CONSTRAINT [FK_printer_product] FOREIGN KEY 
	(
		[model]
	) REFERENCES [dbo].[Product] (
		[model]
	)
GO
----Product------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ 
insert into product values('B','1121','PC')
insert into product values('A','1232','PC')
insert into product values('A','1233','PC')
insert into product values('E','1260','PC')
insert into product values('A','1276','Printer')
insert into product values('D','1288','Printer')
insert into product values('A','1298','Laptop')
insert into product values('C','1321','Laptop')
insert into product values('A','1401','Printer')
insert into product values('A','1408','Printer')
insert into product values('D','1433','Printer')
insert into product values('E','1434','Printer')
insert into product values('B','1750','Laptop')
insert into product values('A','1752','Laptop')
insert into product values('E','2112','PC')
insert into product values('E','2113','PC')
go

                                                                                                                                                                                                                                                                 
----PC------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ 
insert into PC values(1,'1232',500,64,5,'12x',600.00)
insert into PC values(2,'1121',750,128,14,'40x',850.00)
insert into PC values(3,'1233',500,64,5,'12x',600.00)
insert into PC values(4,'1121',600,128,14,'40x',850.00)
insert into PC values(5,'1121',600,128,8,'40x',850.00)
insert into PC values(6,'1233',750,128,20,'50x',950.00)
insert into PC values(7,'1232',500,32,10,'12x',400.00)
insert into PC values(8,'1232',450,64,8,'24x',350.00)
insert into PC values(9,'1232',450,32,10,'24x',350.00)
insert into PC values(10,'1260',500,32,10,'12x',350.00)
insert into PC values(11,'1233',900,128,40,'40x',980.00)
insert into PC values(12,'1233',800,128,20,'50x',970.00)
go

                                                                                                                                                                                                                                                                 
----Laptop------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ 
insert into Laptop values(1,'1298',350,32,4,700.00,11)
insert into Laptop values(2,'1321',500,64,8,970.00,12)
insert into Laptop values(3,'1750',750,128,12,1200.00,14)
insert into Laptop values(4,'1298',600,64,10,1050.00,15)
insert into Laptop values(5,'1752',750,128,10,1150.00,14)
insert into Laptop values(6,'1298',450,64,10,950.00,12)
go

                                                                                                                                                                                                                                                                 
----Printer------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ 
insert into Printer values(1,'1276','n','Laser',400.00)
insert into Printer values(2,'1433','y','Jet',270.00)
insert into Printer values(3,'1434','y','Jet',290.00)
insert into Printer values(4,'1401','n','Matrix',150.00)
insert into Printer values(5,'1408','n','Matrix',270.00)
insert into Printer values(6,'1288','n','Laser',400.00)
go