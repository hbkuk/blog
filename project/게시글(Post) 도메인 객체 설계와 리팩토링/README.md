<div class=markdown-body>

#### [NOW](https://github.com/hbkuk/now-back-end) 프로젝트를 진행하면서 기록한 글입니다.

# 도메인(Domain) 객체 설계  

## 게시글(POST) 도메인 모델링(Domain Modeling)

다음과 같은 요구사항이 주어졌습니다.  
- **게시글은 크게 4가지 종류**로 나눕니다.
    - `공지사항(Notice)`
        - 관리자(Manager)만 작성
        - 핀 설정(상단 고정 여부)
        - 수정 및 삭제
            - 수정 가능
            - 댓글이 있는 경우 삭제 불가능
    - `커뮤니티(Community)`
        - 사용자(User)만 작성
        - 파일 업로드
            - 확장자 **jpg, gif, png, zip**만 허용
            - 크기는 **2MB** 까지만 허용
            - 개수는 **최대 5개**까지
        - 수정 및 삭제
            - 수정 가능
            - 댓글이 있는 경우 삭제 불가능
    - `사진(Photo)`
        - 사용자(User)만 작성
        - 파일 업로드
            - 확장자는 **jpg, gif, png**만 허용
            - 크기는 **1MB** 까지만 허용
            - 개수는 **최대 20개**까지 허용
        - 수정 및 삭제
            - 수정 가능
            - 댓글이 있는 경우 삭제 불가능
    - `문의(Inquiry)`
        - 사용자(User)만 작성
        - 비밀글 설정
            - 본인의 문의글이라면 열람 가능(관리자 열람 가능)
            - 본인의 문의글이 아닐때(관리자 열람 가능)
                - 비밀번호가 동일하다면 열람 가능
                - 비밀번호가 다르다면 열람 불가
        - 비밀글 설정 안함
            - 열람 가능
        - 수정 및 삭제
            - 수정 가능
            - 댓글이 있는 경우 삭제 불가능 

위 게시글의 종류는 **세부적으로 상이하므로 4가지로 분류**합니다. 하지만, **공통적으로 필요로하는 데이터와 기능**이 있습니다. 

---

아래는 공통적으로 필요로하는 데이터의 목록과 기능입니다. 

### 데이터 목록
- **게시글의 고유 식별자**
    - 예시) 1번글, 2번글, 3번글 ...
- **카테고리(코드)**
    - 예시) GRP001-001(공지사항 이벤트 카테고리), GRP001-002(커뮤니티 사는얘기 카테고리)..
- 제목
- 작성자의 아이디
- 작성일자
- 수정일자
- 내용
- 조회수, 좋아요 수, 싫어요 수, 첨부된 파일, 댓글 등..

### 기능
- **게시글 수정**
    - 본인의 게시글이라면 수정 가능
    - 관리자라면 수정 가능
- **게시글 삭제**
    - 본인의 게시글
        - 댓글이 없다면 삭제 가능
        - 댓글이 있으면 삭제 불가능
    - 관리자라면 삭제 가능
- 파일 업로드
    - 다음 포스팅에서...


위에서 요구사항을 분석한 내용을 기반으로 **`도메인 모델링`(Domain Modeling)을 진행**했습니다.  

<br>

![도메인 모델링](https://github.com/hbkuk/now-back-end/assets/109803585/6494d3aa-9a04-49dc-99a7-b5f6b5a07598) 

**공통되는 데이터를 상위 클래스인 Post 도메인 객체에 정의**함으로써,  
각각의 게시글 종류에 대한 **하위 클래스는 공통 필드를 상속받고**, 추가로 **특화된 필드를 갖게 됩니다.** 

그렇다면, 공통 기능인 **게시글 수정 및 삭제에 대한 코드를 확인**해보겠습니다.

아래는 `Post` 도메인 객체에서 구현한 `canDelete()`, `canUpdate()` 메서드입니다.

```
/**
* 게시글을 삭제할 수 있다면 true 반환, 그렇지 않다면 예외를 던짐
*
* @param user     유저 정보가 담긴 객체
* @param comments 댓글 정보가 담긴 객체
* @return 게시글을 삭제할 수 있다면 true 반환, 그렇지 않다면 false 반환
*/
public boolean canDelete(User user, List<Comment> comments) {
    if (!user.isSameUserId(this.authorId)) {
        throw new CannotDeletePostException("다른 사용자가 작성한 게시글을 삭제할 수 없습니다.");
    }

    for (Comment comment : comments) {
        if(!comment.canDelete(user)) {
            throw new CannotDeletePostException("다른 사용자가 작성한 댓글이 있으므로 해당 게시글을 삭제할 수 없습니다.");
        }
    }

    return true;
}

/**
* 게시글을 수정할 수 있다면 true를 반환, 그렇지 않다면 예외를 던짐
*
* @param user      유저 정보가 담긴 객체
* @return          게시글을 수정할 수 있다면 true를 반환, 그렇지 않다면 예외를 던짐
*/
public boolean canUpdate(User user) {
    if (!user.isSameUserId(this.authorId)) {
        throw new CannotUpdatePostException("다른 사용자가 작성한 게시글을 수정할 수 없습니다.");
    }
    return true;
}

```

---

### 테스트 코드


위에서 구현한 **상위 클래스의 메서드인 `canDelete()`와 `canUpdate()`** 메서드에 대해서 테스트 코드를 작성해보겠습니다.  

우선, 테스트를 위해 사용해야 하는 **객체 생성 메서드를 static 메서드로 구현**했습니다. 

```
// PostTest.java
public class PostTest {
    public static Post newPost(String authorId) {
        return Post.builder()
                .postIdx(1L)
                .subCodeIdx(3)
                .subCodeName(3)
                .title("제목")
                .authorId(authorId)
                .regDate(LocalDateTime.now())
                .modDate(LocalDateTime.now())
                .content("내용")
                .viewCount(0)
                .likeCount(0)
                .dislikeCount(0)
                .isCurrentUserPost(false)
                .build();
    }
}
// UserTest.java
public class UserTest {

    public static User newUser(String userId) {
        return User.builder()
                .id(userId)
                .password("testPassword")
                .name("testName")
                .nickname("testNickName")
                .build();
    }
}
// CommentTest.java
public class CommentTest {
    public static Comment newComment(String authorId) {
        return Comment.builder()
                .authorId(authorId)
                .content("contents")
                .postIdx(1L)
                .build();
    }
}
``` 

각각의 도메인 별로 객체를 생성할 때 **인자로 authorId혹은 userId를 전달받는 이유**는, 

**User 도메인 객체의 `id` 필드**와 **게시글 혹은 댓글의 `authorId`가 서로 동일**해야지만,  
**수정 및 삭제가 가능**하기 때문입니다. 

아래는 테스트 코드입니다.  

```
 @Nested
    @DisplayName("canUpdate 메서드는")
    class CanUpdate_of {

        @Test
        @DisplayName("만약 동일한 사용자라면 true를 반환한다.")
        void return_true_when_same_user() {
            // given
            User user = newUser("tester1");
            Post post = newPost("tester1");

            // when, then
            assertThat(post.canUpdate(user)).isTrue();
        }

        @Test
        @DisplayName("만약 다른 사용자라면 CannotUpdatePostException을 던진다.")
        void throw_exception_when_not_same_user() {
            // given
            User user = newUser("tester1");
            Post post = newPost("tester2");

            // when, then
            assertThatExceptionOfType(CannotUpdatePostException.class)
                    .isThrownBy(() -> {
                        post.canUpdate(user);
                    })
                    .withMessageMatching("다른 사용자가 작성한 게시글을 수정할 수 없습니다.");
        }
    }

    @Nested
    @DisplayName("canDelete 메서드는")
    class CanDelete_of {

        @Nested
        @DisplayName("만약 동일한 사용자이면서")
        class SameUser {

            @Test
            @DisplayName("댓글이 하나도 없을 경우 true를 반환한다.")
            void return_true_when_nothing_comment() {
                // given
                User user = newUser("tester1");
                Post post = newPost("tester1");

                // when, then
                assertThat(post.canDelete(user, new ArrayList<Comment>())).isTrue();

            }

            @Test
            @DisplayName("댓글 작성자도 같다면 true를 반환한다.")
            void return_true_when_same_comment_author() {
                // given
                User user = newUser("tester1");
                Post post = newPost("tester1");
                List<Comment> comments = Arrays.asList(newComment("tester1"));

                // when, then
                assertThat(post.canDelete(user, comments)).isTrue();

            }

            @Test
            @DisplayName("댓글 작성자가 다르다면 CanDeletePostException을 던진다.")
            void throw_exception_when_not_same_comment_author() {
                // given
                User user = newUser("tester1");
                Post post = newPost("tester1");
                List<Comment> comments = Arrays.asList(newComment("tester2"));

                // when, then
                assertThatExceptionOfType(CannotDeletePostException.class)
                        .isThrownBy(() -> {
                            post.canDelete(user, comments);
                        })
                        .withMessageMatching("다른 사용자가 작성한 댓글이 있으므로 해당 게시글을 삭제할 수 없습니다.");
            }
        }

        @Nested
        @DisplayName("만약 다른 사용자이면서")
        class NotSameUser {

            @Test
            @DisplayName("댓글이 하나도 없을 경우 CanDeletePostException을 던진다.")
            void throw_exception_when_nothing_comment() {
                // given
                User user = newUser("tester1");
                Post post = newPost("tester2");

                // when, then
                assertThatExceptionOfType(CannotDeletePostException.class)
                        .isThrownBy(() -> {
                            post.canDelete(user, new ArrayList<Comment>());
                        })
                        .withMessageMatching("다른 사용자가 작성한 게시글을 삭제할 수 없습니다.");
            }

            @Test
            @DisplayName("댓글이 있을 경우 CanDeletePostException을 던진다.")
            void throw_exception_when_exist_comment() {
                // given
                User user = newUser("tester1");
                Post post = newPost("tester2");
                List<Comment> comments = Arrays.asList(newComment("tester2"));

                // when, then
                assertThatExceptionOfType(CannotDeletePostException.class)
                        .isThrownBy(() -> {
                            post.canDelete(user, comments);
                        })
                        .withMessageMatching("다른 사용자가 작성한 게시글을 삭제할 수 없습니다.");
            }

            @Test
            @DisplayName("댓글이 같은 사용자일 경우 CanDeletePostException을 던진다.")
            void throw_exception_when_same_comment_author() {
                // given
                User user = newUser("tester1");
                Post post = newPost("tester2");
                List<Comment> comments = Arrays.asList(newComment("tester1"));

                // when, then
                assertThatExceptionOfType(CannotDeletePostException.class)
                        .isThrownBy(() -> {
                            post.canDelete(user, comments);
                        })
                        .withMessageMatching("다른 사용자가 작성한 게시글을 삭제할 수 없습니다.");
            }
        }
``` 
테스트는 모두 성공합니다. 

<br> 


하지만, 여기서 문제가 있습니다. 

**`User` 도메인 객체에 대해서만 고려**하고 있다는 점입니다.  

위에서 봤던 요구사항 중에서는 **관리자**는 **모든 게시물에 대해서 수정 및 삭제가 가능**하다고 했습니다. 

### 매개변수의 데이터 타입

여가서 주의깊게 봐야할 부분은 **`canDelete()`와 `canUpdate()`** 메서드의 **매개변수** 입니다.

![매개변수 데이터 타입](https://github.com/hbkuk/now-back-end/assets/109803585/9d3c1f95-22a3-40b6-ab2a-a43324caab64)

두 메서드에서 **인자로 전달되는 객체의 데이터 타입이 `User`** 이기 떄문입니다.

위에서 봤던 요구사항 중에서는 관리자..  
즉, **`Manager`는 모든 게시물에 대해서 수정 및 삭제가 가능**하다고 했습니다.  

따라서, 두 메서드에서 **관리자 여부를 판단할 수 있어야 합니다.**

그렇다면 다음과 같이 구현할 수 있겠습니다.

```
public boolean canDelete(Object object, List<Comment> comments) {
    if (object instanceof Manager) {
        return true;
    }

    User user = (User) object;
    if(user != null) {

        if (!user.isSameUserId(this.authorId)) {
            throw new CannotDeletePostException("다른 사용자가 작성한 게시글을 삭제할 수 없습니다.");
        }

        for (Comment comment : comments) {
            if (!comment.canDelete(user)) {
                throw new CannotDeletePostException("다른 사용자가 작성한 댓글이 있으므로 해당 게시글을 삭제할 수 없습니다.");
            }
        }
        return true;
    }
    return false;
}

public boolean canUpdate(Object object) {
    if (object instanceof Manager) {
        return true;
    }
    
    User user = (User) object;
    if(user != null) {
        if (!user.isSameUserId(this.authorId)) {
            throw new CannotUpdatePostException("다른 사용자가 작성한 게시글을 수정할 수 없습니다.");
        }
        return true;
    }
    return false;
}

```  

수정된 코드에서는 **`Object` 타입을 인자**로 받고, **`instanceof` 연산자를 사용하여 `Manager` 객체인지 확인**합니다.

만약 **`Manager` 객체라면 `true`를 반환**하고, 그 외에는 **`User` 객체로 캐스팅하여 기존의 로직을 처리**합니다.

아래는 테스트 코드입니다. 

```
@Test
@DisplayName("만약 관리자라면 true를 반환한다.")
void return_true_when_manager() {
    // given
    Manager manager = ManagerTest.newManager("manager1");
    Post post = newPost("tester1");

    // when, then
    assertThat(post.canUpdate(manager)).isTrue();
}


@Test
@DisplayName("만약 관리자라면 항상 true를 반환한다.")
void return_true_when_manager() {
    // given
    Manager manager = ManagerTest.newManager("manager1");
    Post post = newPost("tester1");
    List<Comment> comments = Arrays.asList(newComment("tester1"));

    // when, then
    assertThat(post.canDelete(manager, new ArrayList<Comment>())).isTrue();
    assertThat(post.canDelete(manager, comments)).isTrue();
}
```

테스트는 성공합니다.

![테스트 성공](https://github.com/hbkuk/now-back-end/assets/109803585/0a020a1e-0a35-4af6-bf3c-9db9c285c13d)  

위 코드를 보면... 무언가 **나쁜 냄새(Bad Smell)** 가 납니다.

리팩토링을 해보려고 고민했고, 아래와 같이 진행했습니다. 

<br>

### 클린 하지 못한 코드: 인터페이스를 통한 액세스 권한 제공

![클린하지 못한 코드](https://github.com/hbkuk/now-back-end/assets/109803585/bf02842c-2a39-4457-b896-9711d36ada31)

위 코드에서는 인자로 받는 `object`가 `Manager` 또는 `User` 객체인지 검증하기 위해 **`instanceof` 연산자를 사용**합니다.  

이는 현재의 요구 사항을 충족시키지만, 
**추후에 객체 타입이 추가되거나 변경될 경우 유연성이 떨어질 수 있다고 생각합니다.**  

인자로 받는 객체의 타입을 **인터페이스나 추상 클래스로 정의**하는 것이 좋아보입니다.

따라서, 아래와 같이 인터페이스를 정의하겠습니다.

```
package com.now.domain.permission;

/**
 * 해당 인터페이스는 특정 리소스에 대한 액세스 권한을 나타냄.
 * 구현 클래스는 특정 사용자가 리소스에 액세스할 수 있는지를 확인하는 방법을 제공해야함.
 */
public interface AccessPermission {

    /**
     * 주어진 문자열이 리소스에 액세스할 수 있다면 true 반환, 그렇지 않다면 false 반환
     *
     * @param value 문자열
     * @return 리소스에 액세스할 수 있다면 true 반환, 그렇지 않다면 false 반환
     */
    boolean hasAccess(String value);
}
```

<br>

해당 인터페이스를 구현하는 객체는 **`Manager` 와 `User` 도메인 객체**입니다

```
public class Manager implements AccessPermission {

    private final Long managerIdx;
    private final String id;
    private final String password;
    private final String nickname;

    ...

    /**
     * 접근권한을 있다면 true 반환, 그렇지 않다면 false 반환
     *
     * @param value 문자열
     * @return 접근권한을 있다면 true 반환, 그렇지 않다면 false 반환
     */
    @Override
    public boolean hasAccess(String value) {
        return true;
    }
}

public class User implements AccessPermission {
    
    private static final String passwordRegex = "^(?=.*[a-zA-Z])(?=.*\\d)(?=.*[@#$%^&+=!]).*$";

    private final Long userIdx;
    private final String id;
    private final String password;
    private final String name;
    private final String nickname;

    ...

    /**
     * 전달된 사용자 아이디를 확인해서 동일하다면 true 반환, 그렇지 않다면 false 반환
     *
     * @param userId 사용자 아이디
     * @return 사용자 아이디를 확인해서 동일하다면 true 반환, 그렇지 않다면 false 반환
     */
    @Override
    public boolean hasAccess(String userId) {
        return this.isSameUserId(userId);
    }
}
```

`canDelete` 메서드와 `canUpdate` 메서드는 **`AccessPermission` 인터페이스를 구현한 객체를 인자로 받습니다.** 

해당 객체의 **`hasAccess` 메서드를 호출하여 접근 여부를 확인**합니다.

```
    /**
     * 게시글을 삭제할 수 있다면 true 반환, 그렇지 않다면 예외를 던짐
     *
     * @param accessPermission 접근 권한을 확인하기 위한 AccessPermission 객체
     * @param comments 댓글 정보가 담긴 객체
     * @return 게시글을 삭제할 수 있다면 true 반환, 그렇지 않다면 false 반환
     */
    public boolean canDelete(AccessPermission accessPermission, List<Comment> comments) {
        if (!accessPermission.hasAccess(this.authorId)) {
            throw new CannotDeletePostException("다른 사용자가 작성한 게시글을 삭제할 수 없습니다.");
        }

        for (Comment comment : comments) {
            if (!comment.canDelete(accessPermission)) {
                throw new CannotDeletePostException("다른 사용자가 작성한 댓글이 있으므로 해당 게시글을 삭제할 수 없습니다.");
            }
        }
        return true;
}
    /**
     * 게시글을 수정할 수 있다면 true를 반환, 그렇지 않다면 예외를 던짐
     *
     * @param accessPermission 접근 권한을 확인하기 위한 AccessPermission 객체
     * @return 게시글을 수정할 수 있다면 true를 반환, 그렇지 않다면 예외를 던짐
     */
    public boolean canUpdate(AccessPermission accessPermission) {
        if (!accessPermission.hasAccess(this.authorId)) {
            throw new CannotUpdatePostException("다른 사용자가 작성한 게시글을 수정할 수 없습니다.");
        }
        return true;
    }
```  

이렇게 개선한 코드는 더 명확하고, 확장 가능한 구조를 가집니다.  

또한, 명확하게 분리된 역할과 책임을 갖추고 있습니다.  

리팩토링을 하는 경험을 통해서 테스트 코드가 중요하다는 것을 또 한번 느꼈습니다.  

이상 마치겠습니다.

</div>