# CREATE DATABASE dreamlens_db;

DROP TABLE IF EXISTS Diary;
DROP TABLE IF EXISTS DreamDict;
DROP TABLE IF EXISTS Emotion;
DROP TABLE IF EXISTS DreamType;
DROP TABLE IF EXISTS Interpretation;
DROP TABLE IF EXISTS Users;

CREATE TABLE Diary
(
    id                INT      NOT NULL AUTO_INCREMENT,
    interpretation_id INT      NOT NULL,
    emotion_id        INT      NOT NULL,
    dreamtype_id      INT      NOT NULL,
    date              DATETIME NOT NULL,
    PRIMARY KEY (id)
) COMMENT '꿈 일기장';

CREATE TABLE DreamType
(
    id   INT NOT NULL AUTO_INCREMENT,
    type enum('good', 'bad', 'normal') NULL     COMMENT '길몽/흉몽/일반몽',
    PRIMARY KEY (id)
) COMMENT '꿈 종류';

CREATE TABLE Emotion
(
    id   INT         NOT NULL AUTO_INCREMENT,
    icon VARCHAR(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL     COMMENT '이모티콘',
    name VARCHAR(20) NOT NULL COMMENT '감정 이름',
    PRIMARY KEY (id)
) COMMENT '감정';

ALTER TABLE Emotion
    ADD CONSTRAINT UQ_name UNIQUE (name);

CREATE TABLE Interpretation
(
    id         INT  NOT NULL AUTO_INCREMENT,
    user_id    INT  NOT NULL,
    input_text TEXT NOT NULL COMMENT '꿈 내용',
    result     TEXT NOT NULL COMMENT '해몽 결과',
    keywords   VARCHAR(100) NULL COMMENT '키워드',
    summary    TEXT NULL,
    created_at DATETIME NULL,
    PRIMARY KEY (id)
) COMMENT '해몽 결과 로그';

CREATE TABLE Users
(
    id          INT      NOT NULL AUTO_INCREMENT,
    username    VARCHAR(50)  NOT NULL,
    password    VARCHAR(50)  NOT NULL,
    nickname    VARCHAR(50)  NOT NULL,
    birth       DATE NULL,
    gender      enum('M', 'F', 'N') NULL,
    created_at  DATETIME NOT NULL DEFAULT now(),
    provider    VARCHAR(200) NULL,
    provider_id VARCHAR(200) NULL,
    PRIMARY KEY (id)
) COMMENT '회원';

ALTER TABLE Users
    ADD CONSTRAINT UQ_username UNIQUE (username);

ALTER TABLE Interpretation
    ADD CONSTRAINT FK_Users_TO_Interpretation
        FOREIGN KEY (user_id)
            REFERENCES Users (id)
            ON DELETE CASCADE ;

ALTER TABLE Diary
    ADD CONSTRAINT FK_Interpretation_TO_Diary
        FOREIGN KEY (interpretation_id)
            REFERENCES Interpretation (id);

ALTER TABLE Diary
    ADD CONSTRAINT FK_Emotion_TO_Diary
        FOREIGN KEY (emotion_id)
            REFERENCES Emotion (id);

ALTER TABLE Diary
    ADD CONSTRAINT FK_DreamType_TO_Diary
        FOREIGN KEY (dreamtype_id)
            REFERENCES DreamType (id);
