create database group4;
use group4;

create table lights (
	lamp_id int(5) primary key not null
);

create table groups (
	group_id int(5) primary key not null auto_increment,
	group_name varchar(30) not null,
	unique(group_name)
);

create table light_groups(
	group_id int(5) not null,
	lamp_id int(5) not null,
	primary key (group_id,lamp_id),
	FOREIGN KEY (lamp_id) REFERENCES lights(lamp_id),
	FOREIGN KEY (group_id) REFERENCES groups(group_id),

);

create table light_effects(
	light_id int(5) primary key auto_increment not null,
	light_type ENUM('flash','loop','on') not null,
	light_color varchar(30),
	light_length int(5) default 10,
	unique(light_type,light_color,light_length)
);


create table locations (
	lid int(5) primary key auto_increment not null,
	city varchar(30) not null,
	state varchar(2) not null,
	unique (city,state)
);


create table users(
	user_id int(5) primary key auto_increment not null,
	email varchar(50) not null,
	password varchar(50) not null,
	unique(email),
	lid int(5),
	FOREIGN KEY (lid) REFERENCES locations(lid)
);


create table alerts (
	alert_id int(5) primary key auto_increment not null,
	light_id int(5),
	user_id int(5),
	alert_type ENUM('sun','temp') not null,
	alert_sign int(1) default 1 not null,
	alert_temp int(1) default 0,
	FOREIGN KEY (light_id) REFERENCES light_effects(light_id),
	FOREIGN KEY (user_id) REFERENCES users(user_id)
);


create table current_conditions(
	condition_id int(5) primary key auto_increment not null,
	dt DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	lid int(5),
	sunrise_hour int(2),
	sunrise_minute int(2),
	sunset_hour int(2),
	sunset_minute int(2),
	current_temp int(3),
	FOREIGN KEY (lid) REFERENCES locations(lid)
);






