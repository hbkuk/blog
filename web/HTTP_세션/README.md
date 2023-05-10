<div class="markdown-body">  

# HTTP 쿠키(Cookie)  

쿠키는 어떻게 생겼을까?  

쿠키는 `<이름>=<값>` 형태를 지닌 단순한 문자열이다.  

서버와 브라우저는 기본적으로 **HTTP 메세지 안에 이 쿠키를 담아서 주고 받게 된다.**  

![HTTP 메시지](https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages/httpmsgstructure2.png)

서버는 어떤 쿠키를 브라우저에 저장하고 싶다면 해당 쿠키를 브라우저에 보내줘야 한다.  

HTTP 메시지에 `Set-Cookie` 라는 응답 헤더에 쿠키 정보를 명시하도록 한다.  
여러 개의 쿠키를 보낼때는 다음과 같은 모습이다.

```
Set-Cookie: <이름>=<값>
Set-Cookie: <이름>=<값>
Set-Cookie: <이름>=<값>
```  


이후, 클라이언트는 서버로 HTTP 메세지를 보낼 때, `Cookie` 헤더에 담아서 보낸다.  

만약 여러개의 쿠키를 가지고 있다면 `;`로 구분한다.
```
Cookie: <이름>=<값>; <이름>=<값>; <이름>=<값>
```  

정리하자면,  
- 서버는 **동일한 쿠키를 기준**으로 `Set-Cookie` 헤더를 통해 **최초 1회** 브라우저로 쿠키를 보낸다.
- 이후 브라우저는 `Cookie` 헤더를 통해 모든 요청을 쿠키를 포함해서 보낸다.  


# HTTP 쿠키(Cookie) 송수신 예  
 
상황을 가정해보자.  


서버에서는 클라이언트가 로그인에 성공했을 때는 `logined=true` 라는 쿠키를 보내주고,  
실패했을 때는 `logined=false` 라는 쿠키를 보내주고 싶다.  

이를 통해 서버에서는 다음 요청부터는 해당 클라이언트가 로그인에 성공했는지, 실패했는지 알고싶은 것이다.  
<br>  

우선 **클라이언트가 서버로 로그인 요청을 보낸다.**

`HTTP 요청`(클라이언트 -> 서버)
 ```
GET /login?name=hbk HTTP/1.1
Host: www.test.com
 ```  
<br>  

**해당 요청을 서버에서 받아서, 응답한다.**

`HTTP 응답`(서버 -> 클라이언트)
 ```
HTTP/1.1 200 OK
Content-Type: text/html
Set-Cookie: logined=true
Set-Cookie: name=hbk
 ```  

<br>

HTTP 응답을 받은 브라우저는 쿠키를 하드디스크에 저장한다.  
추후 동일한 서버로 요청을 보낼때마다 Cookie 헤더에 받았던 쿠키를 같이 보낸다.  

```
GET /index.html HTTP/1.1
Host: www.test.com
Cookie: logined=true; name=hbk  
```

이를 통해 서버는 해당 브라우저의 요청에서 쿠키를 확인해서, 로그인 여부에 따라서 다른 페이지를 보여주던지... 원하는 용도로 활용이 가능한 것이다.  

# HTTP 쿠키(Cookie)의 치명적인 문제점  

웹 개발에 대한 약간의 관심이 있는 사람이라면 누구나 브라우저 개발자 도구나 HTTP 분석 도구를 활용해 HTTP 요청, 응답 헤더를 눈으로 볼 수 있다.  

따라서 쿠키를 통해 비밀번호나 이메일 주소와 같은 개인 정보를 전달하는 것은 적합한 방법이 아니다.  

이 같은 쿠키의 단점을 보완하기 위해서 `세션(Session)` 이 등장했다.  

세션은 상태 값으로 유지하고 싶은 정보를 클라이언트인 브라우저에 저장하는 것이 아닌 **서버에 저장**한다.  

서버에 저장한 후 각 클라이언트마다 고유한 아이디를 발급해 이 아이디를 `Set-Cookie` 헤더를 통해 전달한다.  

세션이 상태 데이터를 **웹 서버에서 관리한다는 점**만 다를 뿐 HTTP에서 상태 값을 유지하기 위한 값을 전달할 때는 **쿠키를 사용한다.**  

따라서, 세션은 HTTP의 쿠키를 기반으로 동작한다.  

# HTTP Session 구현  

- 쿠키를 통해 세션 아이디를 전달  
    - 클라이언트가 처음 접근하는 경우 클라이언트가 사용할 **세션 아이디를 랜덤으로 생성**한 후 쿠키를 통해 전달한다.
    - 세션 아이디를 한번 전달하면 이후 요청부터는 상태 값을 공유하기 위해 **해당 세션 아이디를 사용한다.**
    - 세션 아이디가 존재하지 않는다면 **세**션 아이디를 새로 발급한다.**

```
if( request.getSession() == null ) {
    response.addHeader("Set-Cookie", "JSESSIONID=" + UUID.randomUUID() );
}
```  

<br>  

- 모든 클라이언트의 세션 데이터에 대한 저장소  
    - 서버는 **다수의 클라이언트 세션을 지원**해야 한다.
    - 이를 관리할 수 있는 저장소가 필요하다.
    - 모든 세션은 매번 생성하는 것이 아닌, 클라이언트 마다 한번 생성한 후 **재 사용해야 한다.**  

```
public class HttpSessions {
    private static Map<String, HttpSession> sessions = new HashMap<>();

    public static HttpSession getSession(String id) {
        HttpSession session = sessions.get(id);

        if( session == null ) {
            session = new HttpSession(id);
            sessions.put(id, session);
            return session;
        }
        return session;
    }

    static void remove(String id) {
        sessions.remove(id);
    }
}
```  

<br>  

- 클라이언트별 세션 저장소  
```
public class HttpSession {
    private final String id;
    private Map<String, Object> values = new HashMap<>();

    public HttpSession(String id) {
        this.id = id;
    }

    public String getId() {
        return id;
    }

    public void setAttribute(String name, Object value ) {
        values.put(name, value);
    }

    public void getAttribute(String name) {
        values.get(name);
    }

    public void removeAttribute(String name) {
        values.remove(name);
    }

    public void invalidate() {
        HttpSessions.remove(id);
    }
}
```
  
앞서, 클라이언트가 사용할 **세션 아이디를 랜덤으로 생성한 후 쿠키를 통해 전달**했다.

이 접근 방식은몇 가지 잠재적인 보안 위험이 있다.

예를 들어, **세션 ID를 예측**하거나 다른 방법을 통해 얻을 수 있는 경우 악의적인 사용자가 **세션을 하이재킹**하고 사용자로 가장할 수 있다. 이를 **세션 하이재킹 또는 세션 고정 공격이라고 한다.**

보안 문제 외에도 이러한 방식으로 세션을 관리하면 확장성 및 성능 문제가 발생할 수 있습니다.  

이러한 방식으로 **많은 수의 세션이 생성되면 서버에 부담을 주고 프로그램의 성능에 영향을 줄 수 있다는 것**만 우선 알고있자. 

추후, 해당 내용을 보완한 내용으로 다시 포스핑할 예정이다.  

</div>