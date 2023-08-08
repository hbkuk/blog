<div class=markdown-body>

#### [NOW](https://github.com/hbkuk/now-back-end) 프로젝트를 진행하면서 기록한 글입니다.  

<br>

## 기존 세션 기반 인증

이전 포스팅에서는 [HTTP Session](https://starting-coding.tistory.com/631)을 직접 구현해 해보면서, 몇가지의 **보안, 확장성, 성능의 문제가 있다고 생각**했습니다.  

간략하게 다시 적어보자면, 

#### 보안 측면

- **세션 하이재킹 (Session Hijacking)**: 세션 ID를 도용하여 피해자의 세션에 접근하는 공격
- **세션 고정 공격 (Session Fixation)**: 세션 ID를 강제로 주입한 후, 세션 ID로 인증하는 공격

#### 확장 측면

- **세션 불일치**: 서버의 확장으로, 세션 정보를 공유하기 위한 Sticky Session, Session Clustering, 세션 스토리지 외부 분리 등의 작업 요구

따라서, 현재 프로젝트에서는 세션 기반 인증 방식이 아닌 **토큰 기반 인증 방식을 선택**하게 되었습니다.  

### 액세스 토큰(Access Token)과 리프레시 토큰(Refresh Token) 발급  

우선, 토큰을 발급하는 `Request` 형식입니다.

![HTTP-Request-Line](https://github.com/hbkuk/now-front/assets/109803585/a2122113-9a00-4009-9e57-c42192ae3128)  

<br>

회원 확인 후 토큰을 발급하는 핸들러 메서드에서 **해당 `Post` 요청을 처리**합니다.  

![Sign-In메서드](https://github.com/hbkuk/now-front/assets/109803585/b8ad3bf5-e21a-4b5d-8a23-09871828e2f0)  

<br>

`Request`에 성공한다면 다음과 같은 `Response`을 확인할 수 있습니다.

![HTTP-Response](https://github.com/hbkuk/now-front/assets/109803585/dbaaff04-1386-41b9-83fd-6c392a346e5b)  

<br>  

**Request에 성공 시 서버로 부터 전달받은 Response**에 대해서 다시 한번 정리해 보겠습니다.  

- **액세스 토큰(Access Token)**: 보호된 데이터에 대한 접근 권한을 증명하는 값
- **리프레시 토큰(Refresh Token)**: 액세스 토큰 재발급 용도  

<br>

액세스 토큰은 외부에 노출되는 경우 **치명적인 보안 이슈**가 발생합니다.

때문에 만약 탈취되더라도, 악의적인 사용자에 의해 **남용될 수 있는 시간을 최소화 하기 위하여 유효기간이 짧게 설정**합니다.  

<br>

그에 비해, **리프레시 토큰**은 액세스 토큰을 재발급하는 용도로 사용되어야 하므로, **유효기간을 길게** 설정했습니다  

또한, 리프레시 토큰만, **`Http Only` 설정과 `Path` 설정**을 했습니다.

리프레시 **토큰이 필요할 때만 요청**하고 사용하는 것이 쿠키가 노출되는 것을 최소화하는 방법이라고 생각했으며, 이는 **보안 측면에서 중요한 전략**이라고 생각하게 되었습니다.  

(리프레시 토큰이 2개인 이유는 잠시 뒤에..)

<br>

하지만, 다음과 같은 의문이 생길수 있는데요.  

### 악의적인 사용자가 Refresh Token을 탈취해서 Access Token을 발급하는 상황?

HTTP Only로 설정된 **토큰이 탈취**되는 경우는 **주로 네트워크나 통신 경로에서 발생**됩니다.
만약, 클라이언트의 PC가 해킹되었다면 서버에서는 더 이상 할 수 있는 일은 없습니다.

그렇다면 왜 2개의 리프레시 토큰을 발급했던 것일까요?

### 2개의 리프레시 토큰을 발급했던 이유

**보안을 강화** 목적으로 **토큰 블랙리스트를 관리하기 위한 클래스**를 선언해서 사용했습니다.

```
@Component
public class TokenBlackList {
    private final Set<String> accessTokenBlacklist = new HashSet<>();
    private final Set<String> refreshTokenBlacklist = new HashSet<>();

    /**
     * AccessToken을 블랙리스트에 추가
     *
     * @param accessToken 블랙리스트에 추가할 AccessToken
     */
    public void addToAccessTokenBlacklist(String accessToken) {
        accessTokenBlacklist.add(accessToken);
    }

    /**
     * RefreshToken을 블랙리스트에 추가
     *
     * @param refreshToken 블랙리스트에 추가할 RefreshToken
     */
    public void addToRefreshTokenBlacklist(String refreshToken) {
        refreshTokenBlacklist.add(refreshToken);
    }

    /**
     * 주어진 AccessToken이 블랙리스트에 해당 AccessToken이 있으면 true, 그렇지 않으면 false를 반환
     *
     * @param accessToken 확인할 AccessToken
     * @return 블랙리스트에 해당 AccessToken이 있으면 true, 그렇지 않으면 false를 반환
     */
    public boolean isAccessTokenBlacklisted(String accessToken) {
        return accessTokenBlacklist.contains(accessToken);
    }

    /**
     * 주어진 RefreshToken이 블랙리스트에 해당 RefreshToken이 있으면 true, 그렇지 않으면 false를 반환
     *
     * @param refreshToken 확인할 RefreshToken
     * @return 블랙리스트에 해당 RefreshToken이 있으면 true, 그렇지 않으면 false를 반환
     */
    public boolean isRefreshTokenBlacklisted(String refreshToken) {
        return refreshTokenBlacklist.contains(refreshToken);
    }
}
```  

사용하는 이유는 다음과 같습니다.

- **토큰 폐기**: 토큰을 블랙리스트에 추가함으로써, 해당 **토큰을 더 이상 유효하지 않도록 만듦**
- **로그아웃 처리**: 사용자가 **로그아웃**할 때, 해당 토큰을 블랙리스트에 추가하여 **토큰 폐기**
- 세션 관리, 보안 강화.. 등  

<br>

따라서, 다음과 같은 상황에서 토큰 블랙리스트가 사용됩니다.
- `/refresh`: 만료된 액세스 토큰을 리프레시 토큰을 통해 **재발급 시, 기존 토큰 폐기**
- `/log-out`: **사용자가 로그아웃할 때, 해당 토큰 폐기**  

<br>

해당 요청을 담당하고 있는 핸들러 메서드를 살펴보겠습니다.

![토큰-로그아웃](https://github.com/hbkuk/now-front/assets/109803585/428d0eb7-9670-44a3-8caf-6ae8ac9d4224)  

위에서 핸들러 메서드에서 호출한 메서드는 다음과 같습니다.

```
//AuthenticationService.java
/**
* 로그아웃 처리
*
* @param accessToken  로그아웃 대상의 액세스 토큰
* @param refreshToken 로그아웃 대상의 리프레시 토큰
*/
public void logout(String accessToken, String refreshToken) {
    tokenBlackList.addToAccessTokenBlacklist(accessToken);
    tokenBlackList.addToRefreshTokenBlacklist(refreshToken);
}

```

```
// CookieUtil.java
/**
* 쿠키 삭제
*
* @param key 쿠키의 이름 (key)
* @return 삭제되도록 만료 시간이 설정된 쿠키 객체
*/
public static Cookie deleteCookie(String key) {
    Cookie cookie = new Cookie(key, null);
    cookie.setMaxAge(0); // 쿠키의 만료 시간을 0으로 설정
    return cookie;
}
```  

물론, 앞으로 **서버가 확장됨에 따라 다음과 같은 점을 고려**하고자 합니다. 
- **성능 고려**: 블랙리스트가 메모리에 저장되므로, **많은 양의 토큰이 블랙리스트에 쌓일 경우 메모리 부담**
- **동기화**: 여러 서버에서 사용되는 경우, **블랙리스트 정보의 동기화를 유지**
- **유지 관리**: 만료된 토큰은 블랙리스트에서 제거하여 **메모리 점유**

해당 문제에 대해서는 천천히 확장하면서 생각을 하고자 합니다. 

<br>

이제 토큰을 재발급 하는 과정을 간략하게 알려드리고, 마무리하겠습니다.

![토큰 재발급 과정](https://github.com/hbkuk/now-front/assets/109803585/3ce80b19-5b86-4154-98e9-f9bdfc7a1c5d)   

## 마무리

이상으로 현재 프로젝트에서 토큰 기반 인증을 선택한 이유와 어떻게 구현을 했는지에 대해서 간략하게나마 설명드렸습니다.  

부족하거나, 개선할 부분은 앞으로 프로젝트를 진행하면서 차근차근 진행하고자 합니다.  

긴 글 읽어주셔서 감사합니다.

</div>