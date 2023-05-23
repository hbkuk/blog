<div class="markdown-body">  

# Initialized DataBase  

해당 글은 **테스트 환경을 구성**하기 위한 글입니다.  

**톰캣이 실행될 때마다 다음과 같은 작업이 자동화** 됩니다.  

- **기존 테이블을 모두 삭제**
    - DROP TABLE ...
- **테이블 생성**
    - CREATE TABLE ...
- **샘플 데이터 추가**
    - INSERT INTO board (...) VALUES (...) 

<br>

필자의 환경은 다음과 같습니다.  

- Window
- Intellij
- Gradle 
- Tomcat 9.0
- MySQL 8.0  

<br> 

---

### Gradle 의존성 추가  

**sql을 읽어 데이터베이스에 대한 초기화 작업**을 하기 위해 **스프링 프레임워크에서 제공**하는 기능을 활용합니다.  

관련된 모든 의존성에 대해서 기재했습니다.  

#### build.gradle

```
implementation 'org.springframework:spring-core:5.3.10'
implementation 'org.springframework:spring-jdbc:5.3.10'

implementation group: 'javax.servlet', name: 'jstl', version: '1.2'
```  

#### 수동으로 추가한 jar
- Gradle: org.slf4j:slf4j-api:1.7.25  

---

### .sql 파일 위치  

본인이 관리하기 쉬운 위치에 **SQL 파일을 위치**합니다.  

해당 경로를 build.gradle에 다음과 같이 추가합니다.

```
sourceSets {
    main {
        resources {
            srcDirs = ['src/main/resources']
        }
    }
}
```

<br>

###  톰캣 서버가 시작될 때 초기화하도록 ContextLoaderListener 클래스 준비  

```
package com.study.support.context;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.ClassPathResource;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;
import org.springframework.jdbc.datasource.init.ResourceDatabasePopulator;

import javax.servlet.ServletContextEvent;
import javax.servlet.ServletContextListener;
import javax.servlet.annotation.WebListener;

@WebListener
public class ContextLoaderListener implements ServletContextListener {
    private static final Logger logger = LoggerFactory.getLogger(ContextLoaderListener.class);

    @Override
    public void contextInitialized(ServletContextEvent sce) {
        
        DriverManagerDataSource dataSource = new DriverManagerDataSource();
        dataSource.setDriverClassName("com.mysql.jdbc.Driver");
        dataSource.setUrl("jdbc:mysql://localhost:3306/your_database_name");
        dataSource.setUsername("your_username");
        dataSource.setPassword("your_password");

        ResourceDatabasePopulator populator = new ResourceDatabasePopulator();
        populator.addScript(new ClassPathResource("initdb.sql"));

        JdbcTemplate jdbcTemplate = new JdbcTemplate(dataSource);

        try {
            populator.populate(dataSource.getConnection());
        } catch (Exception e) {
            // Handle the exception appropriately
            logger.error("An error occurred while executing database scripts.", e);
        }

        logger.info("Completed Load ServletContext!");
    }

    @Override
    public void contextDestroyed(ServletContextEvent sce) {
    }
}
```  

톰캣 서버가 시작할 때 **`contextInitialized()` 메서드를 호출함으로써, 초기화 작업**이 가능해집니다.  

해당 작업은 **`ContextLoaderListener`는 `ServletContextListener` 인터페이스를 구현하**고 있으며, `@WebListener` 애노테이션 설정이 있기 때문입니다.  

**@WebListener 설정으로 인해 서블릿 컨테이너를 시작하는 과정**에서 **`contextInitialized()` 메서드를 호출**합니다.  

### log 확인  

톰캣을 실행시키고, 로그를 확인하면 다음과 같은 형식의 로그를 확인할 수 있습니다.  

```
11:11:38.355 [RMI TCP Connection(2)-127.0.0.1] DEBUG org.springframework.jdbc.datasource.DriverManagerDataSource - Loaded JDBC driver: com.mysql.jdbc.Driver
11:11:38.419 [RMI TCP Connection(2)-127.0.0.1] DEBUG org.springframework.jdbc.datasource.DriverManagerDataSource - Creating new JDBC DriverManager Connection to [jdbc:mysql://localhost:3316/ebsoft]
11:11:39.060 [RMI TCP Connection(2)-127.0.0.1] DEBUG org.springframework.jdbc.datasource.init.ScriptUtils - Executing SQL script from class path resource [initdb.sql]
11:11:39.107 [RMI TCP Connection(2)-127.0.0.1] DEBUG org.springframework.jdbc.datasource.init.ScriptUtils - 0 returned as update count for SQL: drop table if exists comment
11:11:39.121 [RMI TCP Connection(2)-127.0.0.1] DEBUG org.springframework.jdbc.datasource.init.ScriptUtils - 0 returned as update count for SQL: drop table if exists file
11:11:39.133 [RMI TCP Connection(2)-127.0.0.1] DEBUG org.springframework.jdbc.datasource.init.ScriptUtils - 0 returned as update count for SQL: drop table if exists board
11:11:39.154 [RMI TCP Connection(2)-127.0.0.1] DEBUG org.springframework.jdbc.datasource.init.ScriptUtils - 0 returned as update count for SQL: CREATE TABLE board ( board_idx BIGINT NOT NULL auto_increment, category VARCHAR(100) NOT NULL, title VARCHAR(200) NOT NULL, writer VARCHAR(10) NOT NULL, content VARCHAR(2000) NOT NULL, password VARCHAR(16) NOT NULL, hit INT NOT NULL, regdate DATETIME NOT NULL, moddate DATETIME NULL, PRIMARY KEY (board_idx) )
11:11:39.175 [RMI TCP Connection(2)-127.0.0.1] DEBUG org.springframework.jdbc.datasource.init.ScriptUtils - 0 returned as update count for SQL: CREATE TABLE comment ( comment_idx BIGINT NOT NULL auto_increment, writer VARCHAR(10) NOT NULL, password VARCHAR(16) NOT NULL, content VARCHAR(2000) NOT NULL, regdate DATETIME NOT NULL, board_idx BIGINT NOT NULL, PRIMARY KEY (comment_idx), FOREIGN KEY (board_idx) REFERENCES board (board_idx) )
11:11:39.200 [RMI TCP Connection(2)-127.0.0.1] DEBUG org.springframework.jdbc.datasource.init.ScriptUtils - 0 returned as update count for SQL: CREATE TABLE file ( file_idx BIGINT NOT NULL auto_increment, save_name VARCHAR(255) NOT NULL, original_name VARCHAR(255) NOT NULL, size int NOT NULL, board_idx BIGINT NOT NULL, PRIMARY KEY (file_idx), FOREIGN KEY (board_idx) REFERENCES board (board_idx) )
11:11:39.209 [RMI TCP Connection(2)-127.0.0.1] DEBUG org.springframework.jdbc.datasource.init.ScriptUtils - 3 returned as update count for SQL: INSERT INTO board (board_idx, category, title, writer, content, password, hit, regdate, moddate) VALUES (1, 'JAVA', 'Title 1', '테스터1', 'Content 1', 'password1!', 10, '2023-05-18 10:00:00', null), (2, 'JAVASCRIPT', 'Title 2', '테스터2', 'Content 2', 'password2!', 5, '2023-05-18 11:00:00', null), (3, 'SPRING', 'Title 3', '테스터3', 'Content 3', 'password3!', 8, '2023-05-18 12:00:00', null)
11:11:39.210 [RMI TCP Connection(2)-127.0.0.1] DEBUG org.springframework.jdbc.datasource.init.ScriptUtils - Executed SQL script from class path resource [initdb.sql] in 150 ms.
11:11:39.210 [RMI TCP Connection(2)-127.0.0.1] INFO com.study.support.context.ContextLoaderListener - Completed Load ServletContext!

```



<br>  

</div>