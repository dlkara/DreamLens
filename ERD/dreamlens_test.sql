DELETE FROM dreamlens_core_diary;
ALTER TABLE dreamlens_core_diary AUTO_INCREMENT = 1;
DELETE FROM dreamlens_core_user;
ALTER TABLE dreamlens_core_user AUTO_INCREMENT = 1;
DELETE FROM dreamlens_core_interpretation;
ALTER TABLE dreamlens_core_interpretation AUTO_INCREMENT = 1;


INSERT INTO dreamlens_core_user(username, password, nickname, birth, gender, created_at, provider, provider_id,
                                is_superuser, is_staff, is_active, date_joined, first_name, last_name, email)
VALUES ('test1', '1234', '테테', '2002-07-31', 'F', '2024-10-21', NULL, NULL,
        0, 0, 1, NOW(), '', '', ''),
       ('test2', '1234', '스스', '2010-12-09', NULL, '2025-02-18', NULL, NULL,
        0, 0, 1, NOW(), '', '', ''),
       ('test3', '1234', '트트', '1998-03-15', 'M', '2025-06-30', NULL, NULL,
        0, 0, 1, NOW(), '', '', '')
;


INSERT INTO dreamlens_core_interpretation(user_id, input_text, result, keywords, summary, created_at)
VALUES (1, '꿈 속의 꿈', '불안하신 듯', '꿈, 반복', '불안함', '2025-08-04')
;


INSERT INTO dreamlens_core_diary(user_id, interpretation_id, emotion_id, dream_type_id, date)
VALUES (1, 1, 5, 2, '2025-08-04')
;
