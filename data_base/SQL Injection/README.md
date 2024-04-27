<div class="markdown-body">

# SQL Injection(SQL 삽입)?  

`SQL Injection`은 악의적인 SQL문을 실행되게 함으로써 **데이터 베이스를 비정상적으로 조작하는 코드** 인젝션 공격 방법입니다.  

주로 사용자(Client)가 입력한 데이터를 **서버에서 필터링, 이스케이핑 작업을 스킵**했을 때 발생할 수 있습니다.  

<br>

다음과 같은 `users` 테이블과 데이터가 있습니다.

### 1. `users` 테이블

```
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    age INT,
    email VARCHAR(100),
    password VARCHAR(50)
);
```  

### 2. `users` 테이블의 데이터

<p align="center">
  <img src="https://github.com/hbkuk/blog/assets/109803585/e3469b9b-3230-4df6-948d-2156e5a9db3a" alt="text" width="number" />
</p> 

<br>  

아래와 같은 로그인 화면에 **로그인을 시도**해보겠습니다.  

<p align="center">
  <img src="https://github.com/hbkuk/blog/assets/109803585/ace21bb8-3958-4d88-8887-6ea06b6fa483" alt="text" width="number" />
</p> 

그렇다면, 사용자는 다음과 같이 입력한다고 가정해보겠습니다.   

- Username: Olivia Taylor
- Password: 123  

<br>

이 데이터들은 서버로 전송되며, 서버에서는 **데이터베이스에게 질의**를 합니다.  

<br>

### 이 조건에 맞는 사용자가 있어?  

```
SELECT * FROM users WHERE name = 'Olivia Taylor' AND password = '123'
```  

<br>


즉, 사용자로 부터 전달된 `name`과 `password`로 테이블을 검색했을 때, **정확히 일치하는 사용자가 있다면 로그인 성공처리**를 할 것입니다.  

**데이터 베이스 접근 로직을 살펴보겠습니다.**  

<br>

### SQL Injection이 발생하는 데이터베이스 접근 로직  

```
public class UserDAO {
    ...

    public UserDTO findById(String name, String password) {

        Connection connection = null;
        Statement statement = null;
        ResultSet resultSet = null;

        UserDTO userDTO = new UserDTO();
        try {
            connection = DriverManager.getConnection(this.url, this.user, this.password);

            String queryFormat = "SELECT * FROM users WHERE name = '%s' AND password = '%s'";
            String query = String.format(queryFormat, name, password);
            statement = connection.createStatement();

            resultSet = statement.executeQuery(query);
            if (resultSet.next()) {
                userDTO.setId(resultSet.getLong("id"));
                userDTO.setName(resultSet.getString("name"));
                userDTO.setAge(resultSet.getInt("age"));
                userDTO.setEmail(resultSet.getString("email"));
            }
            return userDTO;
        } catch (SQLException e) {
            e.printStackTrace();
        } finally {
            try {
                if (resultSet != null) {
                    resultSet.close();
                }
                if (statement != null) {
                    statement.close();
                }
                if (connection != null) {
                    connection.close();
                }
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
        return userDTO;
    }
}
```  

`findById` 메서드에 다음과 같은 인자로 전달하여, 실행해보겠습니다.  

- `name`: "Olivia Taylor"
- `password`: "123"  

<br>

```
- 완성되지 않은 쿼리문
    - SELECT * FROM users WHERE name = '%s' AND password = '%s'  

- 완성된 쿼리문
    - SELECT * FROM users WHERE name = 'Olivia Taylor' AND password = '123'  

- 결과
    - id : null	, name : null	, age : 0	, email : null
```  

<br>

입력한 아이디에 해당하는 비밀번호가 서로 다르기 없으며, **일치하는 행이 없기때문에 로그인에 실패**합니다.  

<p align="center">
  <img src="https://github.com/hbkuk/blog/assets/109803585/6d47515f-c104-4edb-921d-5aac3134dbba" alt="text" width="number" />
</p> 

<br>  

만약, **악의적인 사용자가 다음과 같이 값을 입력**한다면 어떻게 될까요?  

<p align="center">
  <img src="https://github.com/hbkuk/blog/assets/109803585/e658444d-fbde-4e51-8e11-4cf05eab8258" alt="text" width="number" />
</p>  

```
- 완성되지 않은 쿼리문
    - SELECT * FROM users WHERE name = '%s' AND password = '%s'  

- 완성된 쿼리문
    - SELECT * FROM users WHERE name = 'Olivia Taylor' AND password = '' or '1' = '1' #'

- 결과
    - id : 1, name : Olivia Taylor	, age : 28	, email : olivia@example.com
```  

### 결과는, **로그인에 성공**하게 됩니다..  

<br>

비밀번호가 다른데, 어떻게 이런 결과가 나왔는지 확인해보겠습니다.  

<br>


<p align="center">
  <img src="https://github.com/hbkuk/blog/assets/109803585/f9434ca9-76ec-4c23-95c9-643056f8862e" alt="text" width="number" />
</p>  

위와 같은 상황에서 **`where`절에서는 조건식이 참이라면, 앞에서의 query는 유효**하게 됩니다.  

그렇다면, 서버는 다음과 같은 쿼리를 **데이테베이스에 질의**하게 됩니다.

```
SELECT * FROM users
```  

<br>

그렇다면, 데이터베이스에서는 다음과 같은 레코드를 반환합니다.  


<p align="center">
  <img src="https://github.com/hbkuk/blog/assets/109803585/e3469b9b-3230-4df6-948d-2156e5a9db3a" alt="text" width="number" />
</p>  

이와 같이 SQL 쿼리문을 주입하는 행위를 **SQL 인젝션** 이라고 부릅니다.  

### SQL 인젝션 공격에 방어하려면?  

```
/*, –, ‘, “, ?, #, (, ), ;, @, =, *, +, union, select, drop, update, from, where, join, substr, user_tables, user_table_columns, information_schema, sysobject, table_schema, declare, dual,…
```  
다음과 같이 **의도치 않은 입력값에 대해서 검증하고 차단**해야합니다.  

<br>

### 준비된 문장인 PreparedStatement을 사용

`PreparedStatement`를 사용하면, **SQL 인젝션 공격에 방어하기 위해 이러한 특수 문자를 이스케이핑**합니다.  

또한, 커넥션을 통해서 미리 **쿼리문을 전송하기 위해서 SQL문장을 준비**하게 되며,  

쿼리문에 활용될 수 있는 **인용 부호가 있다면, 이스케이핑** 하게 됩니다.  

<br>

따라서, 다음과 같이 **데이터 베이스 접근 로직인 DAO 클래스를 수정**할 수 있겠습니다.  

```
    public UserDTO findById(String name, String password) {

        Connection connection = null;
        PreparedStatement preparedStatement = null;
        ResultSet resultSet = null;

        UserDTO userDTO = new UserDTO();
        try {
            connection = DriverManager.getConnection(this.url, this.user, this.password);

            String query = "SELECT * FROM users WHERE name = ? AND password = ?";
            log.info("query: {}", query);

            preparedStatement = connection.prepareStatement(query);
            preparedStatement.setString(1, name);
            preparedStatement.setString(2, password);

            resultSet = preparedStatement.executeQuery();

            if (resultSet.next()) {
                userDTO.setId(resultSet.getLong("id"));
                userDTO.setName(resultSet.getString("name"));
                userDTO.setAge(resultSet.getInt("age"));
                userDTO.setEmail(resultSet.getString("email"));
            }
            return userDTO;
        } catch (SQLException e) {
            e.printStackTrace();
        } finally {
            try {
                if (resultSet != null) {
                    resultSet.close();
                }
                if (preparedStatement != null) {
                    preparedStatement.close();
                }
                if (connection != null) {
                    connection.close();
                }
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
        return userDTO;
    }
```  
</div>