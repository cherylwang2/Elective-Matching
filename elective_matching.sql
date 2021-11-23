use electivematching_db;

-- for refrential integrity add index 

drop table if exists teaches;
drop table if exists chooses;
drop table if exists courses;
drop table if exists user;

create table user (
	uid varchar(15) not null,
	name varchar(30) not null,
	primary key (uid),
	classYear char(4),
	userType enum('student', 'professor'),
	major1 enum('CS', 'DS', 'MAS', 'other'),
    major2 varchar(30),
	minor enum('CS', 'DS', 'MAS', 'other'),
	)

Engine = InnoDB;


create table courses (
	courseid varchar(6) not null,
	name varchar(200) not null,
	capacity tinyint not null,
	waitlistCap tinyint,
	primary key (courseid)
	-- Syllabus fileUpload change this to the correct type 
)

Engine = InnoDB;

create table chooses (
	student varchar not null,
	course int not null,
	rank int not null,
	-- for refrential integrity
	index(uid),
	foreign key (user) references user(uid),
	foreign key (course) references courses(courseid)
	)

Engine = InnoDB;

create table teaches (
	professor varchar not null,
	course int not null,
	-- for refrential integrity
	index(uid),
	foreign key (user) references user(user),
	foreign key (course) references courses(courseid)
)

Engine = InnoDB;
