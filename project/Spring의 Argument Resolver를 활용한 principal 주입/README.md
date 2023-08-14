<div class=markdown-body>

#### [NOW](https://github.com/hbkuk/now-back-end) 프로젝트를 진행하면서 기록한 글입니다.  

<br>

## 기존: 토큰의 클레임 값을 추출하여 요청의 속성으로 설정  

현재 프로젝트에서는 **토큰 기반 인증방식을 선택해서 사용**하고 있습니다.  

[이전 포스팅](https://github.com/hbkuk/blog/tree/main/project/%ED%86%A0%ED%81%B0%20%EA%B8%B0%EB%B0%98%20%EC%9D%B8%EC%A6%9D%EC%9D%84%20%EC%84%A0%ED%83%9D%ED%95%9C%20%EC%9D%B4%EC%9C%A0)에서 소개해드렸습니다.  

<br>  

사용자가 로그인 후에 **게시글을 작성/수정/삭제 할 때, 컨트롤러 진입 전 토큰을 확인**합니다.

유효한 토큰이라면, 다음과 같이 **클레임 값을 추출하여 `HttpServletRequest` 객체 속성을 추가**했는데요.  

![기존 인터셉터](https://github.com/hbkuk/now-back-end/assets/109803585/b66afebd-8a62-4754-bf34-89d63c9c02e5)

<br>  

정상적으로 `HttpServletRequest` 객체 속성을 추가되었다면, **컨트롤러 핸들러 메서드에서는 `@RequestAttribute` 어노테이션을 사용해서 받아**올 수 있었습니다.  

![기존 컨트롤러](https://github.com/hbkuk/now-back-end/assets/109803585/590d085d-1a82-43bd-b8cc-7dcc2a32b269)

<br>  

물론, 인터셉터를 통해 설정된 속성을 받아오는 것이 틀린방법은 아니지만..
코드를 볼 때마다 무언가.. **나쁜 냄새(Bad Smell)가 나는 것 같다는 느낌**을 받았습니다.  

따라서, 해당 로직을 리팩토링하고자 했습니다.  

<br>

## 인증 정보 설정을 `AuthenticationContext`에게 위임  

우선 다음과 같은 클래스를 선언했는데요.

![AuthenticationContext](https://github.com/hbkuk/now-back-end/assets/109803585/b3f8a6aa-a1ae-4f05-8506-ab110275fe67)

해당 객체는 현재 **사용자의 인증 상태를 관리하는 역할**을 하며, **각 요청마다 독립적인 인증 정보를 유지**합니다.  

또한, **Spring 컨테이너에 등록**함으로써, **다른 클래스에서는 해당 클래스를 주입받아 사용**할 수 있습니다. 

<br>

그렇다면, 기존 인터셉터 로직을 수정해보도록 하겠습니다.  

![리팩토링된 인터셉터](https://github.com/hbkuk/now-back-end/assets/109803585/a9b18d5f-b5f7-45a2-b266-38007e5e00f1)

<br>

이제, 이렇게 설정한 인증 정보를 **컨트롤러 메소드 파라미터에 바인딩될 수 있게 Argument Resolver 구현**해줘야합니다.

<br>  

## Argument Resolver 구현 

Argument Resolver 구현하기 위해서는 다음과 같은 **`HandlerMethodArgumentResolver` 인터페이스를 구현**해야하는데요.  

![클래스 선언](https://github.com/hbkuk/now-back-end/assets/109803585/bc8f1d4a-990d-4750-9a63-c32cd91fa4ce)

<br>

우선, **`HandlerMethodArgumentResolver`** 인터페이스에 대한 문서를 살펴보겠습니다.  

![HandlerMethodArgumentResolver](https://github.com/hbkuk/now-back-end/assets/109803585/9e3bf7ad-f782-4e41-b349-d58c4b16898b)  

<br>

해당 인터페이스는 두 개의 메서드를 가지고 있는데요.  

- `supportsParameter`: 주어진 메소드의 파라미터가 이 **Argument Resolver에서 지원한다면 true 를, 그렇지 않다면 false 를 반환**
- `resolveArgument`: 메소드의 반환값이 대상이 되는 **메소드의 파라미터에 바인딩**  

<br>  

해당 인터페이스를 구현해보겠습니다.  

![인터페이스 구현](https://github.com/hbkuk/now-back-end/assets/109803585/af6bc282-92f2-413c-9c59-ac91361c3d5e)  

<br>  

## AuthenticationConfig에서 Argument Resolver 등록  

그 다음으로는, **구현한 클래스를 `AuthenticationConfig`에 등록**했습니다.  

![Config 추가](https://github.com/hbkuk/now-back-end/assets/109803585/7ffdd348-0c59-47e8-a979-3abeb312bf71)  

<br>  

## 컨트롤러 핸들러 메소드 파라미터에 바인딩된 객체

![어노테이션없이 컨트롤러 사용](https://github.com/hbkuk/now-back-end/assets/109803585/c418dc7f-62f8-466e-a40d-47b3aae522cc)  

그렇다면, 컨트롤러 핸들러 메서드에서는 **데이터 타입이 `AuthenticationContext`인 파라미터에 바인딩됩니다.**  

<br>  

여기서, 저는 개선해야할 부분이 몇가지 있다고 느꼈는데요.  
- **특정한 상황에서만 바인딩되도록 개선**
- 데이터 타입이 **`String`인 `principal` 필드를 바인딩하도록 개선**  

<br>

그 이유는, 
- 인증 정보가 필요한 **모든 컨트롤러는 `AuthenticationContext` 객체와의 의존관계를 굳이 가져야할까?** 
- 인증 정보가 필요한 **모든 컨트롤러마다 `getPrincipal()` 메서드를 호출해서 매번 값을 꺼내야할까?**  

<br>

따라서, 다음과 같이 사용될 수 있도록 개선해보고자 했습니다.  

![어노테이션이 적용된 컨트롤러 사용](https://github.com/hbkuk/now-back-end/assets/109803585/809dac60-f233-4be2-afbc-0b96941925ae)  

<br>  

## 어노테이션 선언  

다음과 같이 특정한 상황에서만 객체에 바인딩 될 수 있도록 **어노테이션을 선언**했습니다.

![어노테이션 선언](https://github.com/hbkuk/now-back-end/assets/109803585/579ee82b-53eb-4592-8bdf-4956ae7f1fec)   

<br>  

그렇다면, 전에 구현했던 **Argument Resolver를 수정**해야 하는데요.  
다음과 같이 수정했습니다.  

![개선된 Resolver](https://github.com/hbkuk/now-back-end/assets/109803585/1069bccc-f176-4f63-a55d-6d17bc4a0a7b)  

<br>  

## 마무리  

리팩토링을 통해서 코드의 구조화와 가독성을 향상시키는 데 큰 도움이 되었습니다.

부족한 내용이지만, 제가 어떤식으로 리팩토링하는 과정을 겪었는지에 대해서 조금이나마 이해가 되셨다면 좋겠습니다.

긴 글 읽어주셔서 감사합니다.


</div>