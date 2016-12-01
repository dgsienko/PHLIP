create database group4;
use group4;



create table light_effects(
	light_id int(5) primary key auto_increment not null,
	light_type ENUM('flash','loop','on') not null,
	light_color varchar(30),
	light_length int(5) default 10
);


create table locations (
	lid int(5) primary key auto_increment not null,
	city varchar(30) not null,
	state varchar(2) not null,
	unique (city,state)
);


create table alerts (
	alert_id int(5) primary key auto_increment not null,
	light_id int(5),
	alert_type ENUM('sun','temp') not null,
	alert_sign int(1) default 1 not null,
	alert_temp int(1) default 0,
	FOREIGN KEY (light_id) REFERENCES light_effects(light_id)
);


create table current_conditions(
	condition_id int(5) primary key auto_increment not null,
	ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	sunrise_hour int(2),
	sunrise_minute int(2),
	sunset_hour int(2),
	sunset_minute int(2),
	current_temp int(3)
);


create table users(
	user
	location


);

