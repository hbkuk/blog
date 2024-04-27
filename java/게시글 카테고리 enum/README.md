<div class=markdown-body>  

#### [NOW](https://github.com/hbkuk/now-back-end) 프로젝트를 진행하면서 기록한 글입니다.  

## 게시글의 카테고리를 DB에서 관리하다

하나의 게시글을 DB에 저장한다고 하면,  
해당 글이 **공지 글인지, 커뮤니티 글인지, 사진 글인지, 문의 글인지 구분**해야합니다.  

**게시글 테이블의 카테고리 컬럼을 추가해서 해결**할 수도 있겠지만, 
**게시글 카테고리에 한정하지 않고**, 서비스 내에서 사용할 **카테고리성 데이터에도 사용할 수 있도록 테이블을 설계**해야 한다고 생각했습니다.  

다음과 같은 용도로요.  

![숫자형코드 테이블](https://github.com/hbkuk/now-back-end/assets/109803585/f9f40f42-2a92-4e2e-9285-ae7e94d206f4)
> 출처: 우아한기술블로그(https://techblog.woowahan.com/2527/)

따라서,
**현재 초기 프로젝트의 테이블 구조**입니다.

![초기 테이블 구조](https://github.com/hbkuk/now-back-end/assets/109803585/183e4000-d321-41ce-938a-62d45ce27504)  

<br>

게시글 카테고리에 사용할 데이터를 **코드 그룹(tb_code_group)과 하위 코드 테이블(tb_sub_code)에서 다음과 같이 관리**했습니다.

![테이블 데이터](https://github.com/hbkuk/now-back-end/assets/109803585/526ff994-d6e2-42b7-a704-0980c3b9e89c)  

<br>

## 게시글 작성

그렇다면, 사용자의 요청으로부터 게시글이 작성되는 흐름에 대해서 확인해보겠습니다.

아래와 같이 **문의 게시글 작성 요청을 받는 Post 컨트롤러의 핸들러 메서드**가 있습니다.

![컨트롤러 핸들러 메서드](https://github.com/hbkuk/now-back-end/assets/109803585/54fe4165-5220-4455-b2eb-f09f432524d3)

```
@PostMapping("/api/inquiry")
public ResponseEntity<Void> registerInquiryPost(@RequestAttribute("id") String userId,
                                                @RequestBody
                                                @Validated(PostValidationGroup.register.class) Inquiry inquiry) {
    log.debug("registerInquiryPost 호출, userId : {}, inquiry : {}", userId, inquiry);

    postService.registerInquiryPost(inquiry.updateAuthorId(userId));
    return ResponseEntity.status(HttpStatus.CREATED).build(); // Status Code 201
}
```  

<br>

클라이언트는 다음과 같은 **JSON 형식으로 요청을 하고, 서버에서는 `Inquiry` 객체에 mapping**합니다.

```
{
    "subCode": "GRP004-001",
    "title": "테스트 제목",
    "content": "테스트 내용",
    "secret": "true"
}
```

<br>  

다음으로는, 
`postService` 객체의 `registerInquiryPost` 메서드를 호출했습니다.

![서비스 메서드 로직](https://github.com/hbkuk/now-back-end/assets/109803585/1782f7b6-a1e2-4aa3-973b-90342f861ba5)


**서비스 객체에서는 다음과 같이 코드**를 나눌 수 있습니다. 
- **사용자 확인**
- 전달받은 **하위 카테고리로 문의 카테고리 그룹인지 확인**
- DB에 저장하기 위해 **하위 카테고리를 하위 카테고리 테이블의 고유 식별자로 변환**
- **DB 저장**  

<br>

전달받은 **하위 카테고리로 문의 카테고리 그룹인지 확인하는 쿼리**입니다. 

```
<select id="checkInquiryGroupCode" resultType="java.lang.Boolean">
    SELECT COUNT(*) > 0
    FROM tb_code_group cg
                JOIN tb_sub_code sc ON sc.code_group_idx = cg.code_group_idx
    WHERE cg.code = 'GRP004' AND sc.code = #{subCode}
</select>
```  

그렇다면, **문의 게시글 뿐만 아니라, 공지, 커뮤니티, 사진 .. 게시글** 또한, 위와 같은 **쿼리문이 별도로 있어야한다는** 의미이고, **매번 카테고리 고유 식별자로 변환**해야합니다. 

...


저는 이러한 상황에서 다음과 같은 고민을 하게되었습니다. 

## 현재 코드 테이블의 문제  

- **카테고리의 수정 및 삭제가 빈번**할까?
- **굳이 복잡하게 DB에서 관리해야하는 이점**이 뭘까?  

<br>

"**굳이 DB에서 관리할 필요가 없다**" 라는게 결론이었습니다..

<br>

저는 이러한 문제를 **`Enum`으로 해결할 수 있겠다고 생각**했습니다.

따라서, **게시글 카테고리 데이터를 Enum으로 전환**하게 되었습니다.  

<br>  

## 관리 주체를 기존 DB에서 Enum으로

![초기 enum으로 변경](https://github.com/hbkuk/now-back-end/assets/109803585/4a32ee56-1675-4e93-aa60-76fc639167c6)


**Java의 `Enum`은** 결국 클래스인 점을 이용하여, **Enum 상수에 카테고리 문자열 리스트**를 갖도록 하였습니다.
각 Enum 상수들은 본인들이 갖고 있는 문자열들을 확인하여 문자열 인자값이 **어느 Enum 상수에 포함되어있는지 확인**할 수 있게 되었습니다.

기존에 DB에게 물어봤던 내용을, **앞으로는 `PostGroup`에게 물어보면 됩니다.**
![초기 enum 테스트 코드](https://github.com/hbkuk/now-back-end/assets/109803585/fb70468a-5215-42d8-aa14-c11860cec30c)

모든 테스트는 성공합니다.
![테스트 성공](https://github.com/hbkuk/now-back-end/assets/109803585/8301bd22-3401-47f1-aa60-f54a49aedc9e)


여기까지 진행 후 Enum의 코드를 보니 해결하지 못한 문제가 있다는 것을 확인했습니다.

그것은..**카테고리의 데이터 타입이 String(문자열) 이라는 것**입니다.

**DB 테이블의 카테고리 컬럼에 잘못된 문자열을 등록**하거나,
**파라미터로 전달된 값이 잘못되었을 경우가 있을 때** 전혀 관리가 안됩니다.

그래서 이 **카테고리 역시 `Enum`으로 전환**하였습니다.

![개선된 enum](https://github.com/hbkuk/now-back-end/assets/109803585/8006e3c0-6f16-4750-83d9-d5455e28ab6b)

이렇게 `Enum`으로 카테고리를 만들고, `PostGroup`에서 이를 사용하도록 하겠습니다.

![개선된 enum 테스트 코드](https://github.com/hbkuk/now-back-end/assets/109803585/ee7883d8-b0ca-48b1-a74f-e3cd2d8533cd)


이렇게, **타입 안전성**까지 확보하여 **`PayGroup`에서 관련된 처리를 진행**할 수 있게 되었습니다.


그렇다면 테스트 코드가 아닌 실제로 사용되는 코드에 대해서 소개해드리고 마무리하겠습니다.

## 개선된 게시글 등록

![JSON 요청](https://github.com/hbkuk/now-back-end/assets/109803585/9d52a4cc-1290-41dc-9f88-3168eb44e5a9)

우선, 클라이언트에서 **`JSON` 형태로 다음과 같이 요청**할 수 있습니다.

고려해야할 사항으로는
스프링에서 제공하는 기능 중 **요청 본문에 포함된 데이터를 객체로 매핑해주는 `객체 바인딩`** 에서 **Enum은 자동적으로 진행하지 않다는 점입니다.**

따라서, 
Enum을 **매핑하기 위해서는 추가적인 작업이 필요**합니다.  

<br>

저는, **`Enum` 값을 JSON으로 변환**하거나 **JSON 값을 `Enum`으로 변환**하기 위해 Jackson 라이브러리에서 제공하는 **`@JsonValue`와 `@JsonCreator` 어노테이션을 사용**했습니다.  

![JSON ENUM mapping 객체](https://github.com/hbkuk/now-back-end/assets/109803585/f301a559-dea8-437d-b03c-07285b2be921)

아래와 같이 **문의 게시글 작성 요청을 받는 Post 컨트롤러의 핸들러 메서드**가 있습니다.
![컨트롤러 메서드](https://github.com/hbkuk/now-back-end/assets/109803585/3f7f9b16-4afd-449b-bc8e-974763d598a2)

다음으로는, 
`postService` 객체의 `registerInquiryPost` 메서드를 호출했습니다.

![서비스 메서드](https://github.com/hbkuk/now-back-end/assets/109803585/08c49518-3f32-4d30-833c-0dfbaf0759e7)

## 마무리 
이렇게 기존에 DB에서 관리하는 데이터를 Enum으로 관리하는 데이터로 변경해보았습니다. 

무조건적으로 **"카테고리는 Enum으로 관리해야해."** 는 아니지만,

**빈번하게 변경되지도 않는 데이터를 굳이 DB에서 관리할 필요가 있을까?** 라는 고민이 생겼고, 해결한 경험이 하나 생겼다는 것에 만족합니다.

앞으로도, 위와 같은 상황이 찾아온다면 **`Enum`을 적극적으로 사용**할 것입니다. 

하지만, 무조건적으로 Enum을 사용하는 것은 아니고, 여러가지 문제를 따져보고 해야하곘지만요.

긴 글 읽어주셔서 감사합니다.

#### 참고
1) Java Enum 활용기: https://techblog.woowahan.com/2527/

</div>