CREATE TABLE Diary
(
    id                INT      NOT NULL AUTO_INCREMENT,
    interpretation_id INT      NOT NULL,
    emotion_id        INT      NOT NULL,
    dreamtype_id      INT      NOT NULL,
    date              DATETIME NOT NULL,
    PRIMARY KEY (id)
) COMMENT '꿈 일기장';

CREATE TABLE DreamDict
(
    id       INT     NOT NULL AUTO_INCREMENT,
    category VARCHAR NOT NULL COMMENT '대분류',
    keyword  VARCHAR NOT NULL COMMENT '소분류 키워드',
    meaning  TEXT    NOT NULL COMMENT '상징적 의미',
    PRIMARY KEY (id)
) COMMENT '꿈 사전';

ALTER TABLE DreamDict
    ADD CONSTRAINT UQ_keyword UNIQUE (keyword);

CREATE TABLE DreamType
(
    id   INT NOT NULL AUTO_INCREMENT,
    type VARCHAR(10) NULL     COMMENT '길몽/흉몽/일반몽',
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
    input_text TEXT NOT NULL COMMENT '꿈 내용',
    result     TEXT NOT NULL COMMENT '해몽 결과',
    summary    TEXT NULL,
    created_at DATETIME NULL,
    user_id    INT  NOT NULL,
    PRIMARY KEY (id)
) COMMENT '해몽 결과 로그';

CREATE TABLE InterpretationKeyword
(
    id                INT NOT NULL AUTO_INCREMENT,
    interpretation_id INT NOT NULL,
    dict_id           INT NOT NULL,
    PRIMARY KEY (id)
) COMMENT '해몽결과에 포함된 키워드';

CREATE TABLE User
(
    id          INT      NOT NULL AUTO_INCREMENT,
    username    VARCHAR  NOT NULL,
    password    VARCHAR  NOT NULL,
    nickname    VARCHAR  NOT NULL,
    birth       DATE NULL,
    gender      VARCHAR NULL,
    created_at  DATETIME NOT NULL DEFAULT now(),
    provider    VARCHAR NULL,
    provider_id VARCHAR NULL,
    PRIMARY KEY (id)
) COMMENT '회원';

ALTER TABLE User
    ADD CONSTRAINT UQ_username UNIQUE (username);

ALTER TABLE Interpretation
    ADD CONSTRAINT FK_User_TO_Interpretation
        FOREIGN KEY (user_id)
            REFERENCES User (id);

ALTER TABLE InterpretationKeyword
    ADD CONSTRAINT FK_Interpretation_TO_InterpretationKeyword
        FOREIGN KEY (interpretation_id)
            REFERENCES Interpretation (id);

ALTER TABLE InterpretationKeyword
    ADD CONSTRAINT FK_DreamDict_TO_InterpretationKeyword
        FOREIGN KEY (dict_id)
            REFERENCES DreamDict (id);

ALTER TABLE Diary
    ADD CONSTRAINT FK_Interpretation_TO_Diary
        FOREIGN KEY (interpretation_id)
            REFERENCES Interpretation (id);

ALTER TABLE Diary
    ADD CONSTRAINT FK_User_TO_Diary
        FOREIGN KEY (user_id)
            REFERENCES User (id);

ALTER TABLE Diary
    ADD CONSTRAINT FK_Emotion_TO_Diary
        FOREIGN KEY (emotion_id)
            REFERENCES Emotion (id);

ALTER TABLE Diary
    ADD CONSTRAINT FK_DreamType_TO_Diary
        FOREIGN KEY (dreamtype_id)
            REFERENCES DreamType (id);
