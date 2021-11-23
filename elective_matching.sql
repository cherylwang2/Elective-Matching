use electivematching_db;

drop table if exists teaches;
drop table if exists chooses;
drop table if exists courses;
drop table if exists user;

create table user (
	uid varchar(15) not null,
	name varchar(30) not null,
	classYear char(4),
	userType enum('student', 'professor'),
	major1 enum('CS', 'DS', 'MAS', 'other'),
    major2 varchar(30),
	minor enum('CS', 'DS', 'MAS', 'other'),
	primary key(uid)
)
Engine = InnoDB;

create table courses (
	courseid varchar(6) not null,
	name varchar(200) not null,
	capacity tinyint not null,
	waitlistCap tinyint not null,
	primary key(courseid)
)
Engine = InnoDB;

create table chooses (
	student varchar(15) not null,
	course varchar(6) not null,
	courseRank int not null,
	index(student),
	foreign key (student) references user(uid),
	foreign key (course) references courses(courseid)
	)
Engine = InnoDB;

create table teaches (
	professor varchar(15) not null,
	course varchar(6) not null,
	index(professor),
	foreign key (professor) references user(uid),
	foreign key (course) references courses(courseid)
)
Engine = InnoDB;
