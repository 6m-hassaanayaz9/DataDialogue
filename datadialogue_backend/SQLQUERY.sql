-- database: d:\FYP_DATA\FYP_Project\datadialgue_bckend\datadialgue_bckend\db.sqlite3

-- Use the ▷ button in the top right corner to run the entire file.

CREATE TABLE user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL
);

CREATE TABLE database (
    database_id INT AUTO_INCREMENT PRIMARY KEY,
    database_name VARCHAR(255) NOT NULL,
    access_key VARCHAR(255),
    connection_string VARCHAR(255) NOT NULL
);

CREATE TABLE access_list (
    user_id INT,
    database_id INT,
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (database_id) REFERENCES database(dataas),
    PRIMARY KEY (user_id,database_id)
);



CREATE TABLE conversation(
    conversation_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    database_id INT,
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (database_id) REFERENCES database(database_id)

);


CREATE TABLE message(
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    conversation_id INT,
    question TEXT,
    answer TEXT,
    time_stamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversation(conversation_id)

); 


CREATE TABLE prompt(
    prompt_id INT AUTO_INCREMENT PRIMARY KEY,
    prompt_data TEXT,
    database_id INT,
    FOREIGN KEY (database_id) REFERENCES database(database_id)
);-- database: c:\Users\Ammar Younas\Desktop\New folder\dataDialogue.db