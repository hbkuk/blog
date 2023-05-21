<div class="markdown-body">

# 데이터 베이스 커넥션  

___해당 글은 데이터베이스 커넥션 풀 (DBCP)에 대해서는 다루지 않습니다.___  

<p align="center">
  <img src="https://github.com/hbkuk/blog/assets/109803585/4903b40e-523d-4ced-8bba-e8ed1a2a9606" alt="text" width="number" />
</p>  

<br>

웹 애플리케이션과 데이터베이스는 서로 다른 시스템이며, 데이터베이스 드라이버를 사용하여 데이터베이스에 연결해야 합니다.  

**데이터베이스 연결의 생애주기**는 다음과 같습니다.  

- 데이터베이스 드라이버를 사용하여 **데이터베이스 연결 열기**
- 데이터를 읽고 쓰기 위해 **TCP 소켓 열기**
- **TCP 소켓을 사용하여 데이터 통신**
- 데이터베이스 **연결 닫기**
- **TCP 소켓 닫기**  

위와 같이 데이터베이스 연결을 수립하고, 해제하는 과정은 비용이 많이 들어가는 작업입니다.  

<br>

## DAO 클래스의 Connection 객체  

아래 설명할 코드는 **데이터베이스 접근 로직을 담당하는 DAO 클래스**입니다.  

주의깊게 봐야할 점은 <u>**전역변수로 관리하고 있는 Connection 객체**</u>입니다.  

<p align="center">
  <img src="https://github.com/hbkuk/blog/assets/109803585/9fd420e7-4a36-48f2-9db3-00a6150ee8e4" alt="text" width="number" />
</p>  

`BoardDAO` 객체가 생성된다면 다음과 같은 상황이 발생합니다.  

- `Class.forName()` 메서드를 통해서 클래스가 로딩될 때 **자동으로 JDBC 드라이버가 등록됩니다.**
- `DriverManager.getConnection()` 메서드를 통해 **데이터베이스에 대한 연결을 나타내는 Connection 객체를 반환**받는다.
- 전역 변수인 `connection`에 반환 받은 **Connection 객체를 할당**한다.  

<br>

## 전역 Connection의 문제점  

- `Thread 안정성`: 여러 Thread가 동시에 BoardDAO에 접근하는 경우 **전역 Connection 객체가 공유 리소스**가 될 수 있습니다.  
이로 인해 동시 액세스 문제 및 경합 상태가 발생하여 **데이터 불일치 또는 오류가 발생**할 수 있습니다.  
- `리소스 누수`: 여러 메서드가 연결을 닫지 못하거나 예외가 발생하면 리소스가 해제되지 않아 **리소스 누수가 발생하고 결국 연결 풀에서 사용 가능한 연결이 고갈**될 수 있습니다.  
- `비효율적인 자원 활용`: 사용되지 않는 경우에도 열린 상태로 유지되어 자원 활용이 비효율적일 수 있습니다.
- `오류 처리에 대한 유연성 어려움`: 연결 생성 또는 사용 중에 발생하는 오류는 클래스 전체에 전파될 수 있으므로 정상적으로 처리하기가 어려워집니다.  

<br>

`Connection`을 전역 변수로 관리하면 위와 같은 문제가 발생하여 데이터 불일치, 리소스 누수, 성능 저하 및 오류 처리 기능 제한과 같은 문제가 발생할 수 있습니다.  

### 따라서, 로컬 변수를 사용하고 각 방법의 범위 내에서 연결을 설정 및 해제하는 것이 좋습니다.  

<br>

## 지역변수로 Connection을 선언한 코드

```
public class BoardDAO {

    public BoardDTO findById(Long id) {
        Connection connection = null;
        PreparedStatement statement = null;
        ResultSet resultSet = null;
        BoardDTO boardDTO = null;

        try {
            connection = DriverManager.getConnection(jdbcUrl, username, password);
            statement = connection.prepareStatement("SELECT * FROM board WHERE board_idx = ?");
            statement.setLong(1, id);
            resultSet = statement.executeQuery();

            if (resultSet.next()) {
                boardDTO = new BoardDTO();
                boardDTO.setBoardIdx(id);
                boardDTO.setCategory(Category.valueOf(resultSet.getString("category")));
                boardDTO.setTitle(resultSet.getString("title"));
                boardDTO.setWriter(resultSet.getString("writer"));
                boardDTO.setContent(resultSet.getString("content"));
                boardDTO.setPassword(resultSet.getString("password"));
                boardDTO.setHit(resultSet.getInt("hit"));
                boardDTO.setRegDate(resultSet.getTimestamp("regdate").toLocalDateTime());
                if (resultSet.getTimestamp("moddate") != null) {
                    boardDTO.setModDate(resultSet.getTimestamp("moddate").toLocalDateTime());
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        } finally {
            if (resultSet != null) {
                try {
                    resultSet.close();
                } catch (SQLException e) {
                    e.printStackTrace();
                }
            }
            if (statement != null) {
                try {
                    statement.close();
                } catch (SQLException e) {
                    e.printStackTrace();
                }
            }
            if (connection != null) {
                try {
                    connection.close();
                } catch (SQLException e) {
                    e.printStackTrace();
                }
            }
        }
        return boardDTO;
    }
}
```







</div>