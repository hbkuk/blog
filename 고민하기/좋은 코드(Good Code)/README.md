<div class=markdown-body>

## 좋은 코드(Good Code)에 대해서

개발자 라는 직업을 선택하고나서,

매일 코드를 보고있고, 코드를 작성하고 있지만 단 한번도 좋은 코드에 대해서 진지하게 고민을 해본적이 없었다.

이번 기회를 통해서 스스로에게 물어보고 대답한 것을, 문서로 남기고자 한다.

## 내가 생각한 좋은 코드란 무엇일까?

- 읽기 쉬운 코드
- 역할과 책임이 명확하게 분리된 코드
- 테스트 가능한 코드


### 1. 읽기 쉬운 코드  

나는 읽기 쉬운 코드를 만들기 위해서 몇가지 규칙을 가지고 있다.

- 명확한 변수 혹은 메서드 이름을 사용하기
- 줄 바꿈 활용하기
- 주석을 상세하기 적어놓기

어떤식으로 이를 적용했는지 코드로 살펴보자.  

<br>

#### 1-1. 명확한 변수 혹은 메서드 이름을 사용하기

아래 클래스는 커뮤니티 게시글을 나타내는 도메인 클래스다.

```
public class Community {

    ...
    private final String title;
    private final String content;
    private final List<Comment> comments;
    private String memberId;

    public boolean canUpdate(Member member) {
        if (!member.isSameMemberId(this.memberId)) {
            throw new CannotUpdatePostException(ErrorType.CAN_NOT_UPDATE_OTHER_MEMBER_POST);
        }
        return true;
    }

    public boolean canDelete(Member member, List<Comment> comments) {
        if (!member.isSameMemberId(this.memberId)) {
            throw new CannotDeletePostException(ErrorType.CAN_NOT_DELETE_OTHER_MEMBER_POST);
        }

        for (Comment comment : comments) {
            if (!comment.canDelete(member)) {
                throw new CannotDeletePostException(ErrorType.CAN_NOT_DELETE_POST_WITH_OTHER_MEMBER_COMMENTS);
            }
        }
        return true;
    }
}

```  

위처럼, 메서드명을 `canUpdate`, `canDelete` 와 같이 메서드가 하는 일을 명확하게 나타내고 있다.  

`canUpate` 메서드는 게시글을 수정할 수 있는지를 판단하고,
`canDelete` 메서드는 게시글을 삭제할 수 있는지를 판단한다.  

#### 1-2. 들여쓰기와 공백 활용하기  

![공백](https://github.com/hbkuk/java-unit-testing/assets/109803585/aac21cc3-57dd-454f-ac79-ce51dd54fec1)

위 코드를 보면, 줄 바꿈(Line Breaks)을 활용해서 메서드 내의 코드를 그룹화하고 경계를 명확하게 만들어서 코드를 이해하기 쉽도록 만들었다.

#### 1-3. 주석을 상세하기 적어놓기  

위에서는 지워놨지만, 원래 메서드마다 주석을 적는다.

```
/**
* 게시글을 수정할 수 있다면 true 반환, 그렇지 않다면 false 반환
*
* @param member 수정을 시도하는 회원
* @return 게시글을 수정할 수 있다면 true 반환, 그렇지 않다면 false 반환
* @throws CannotUpdatePostException 다른 회원이 작성한 게시글을 수정할 수 없을 때 예외 발생
*/
public boolean canUpdate(Member member) {
    if (!member.isSameMemberId(this.memberId)) {
        throw new CannotUpdatePostException(ErrorType.CAN_NOT_UPDATE_OTHER_MEMBER_POST);
    }
    return true;
}

/**
* 게시글을 삭제할 수 있다면 true 반환, 그렇지 않다면 false 반환
*
* @param member   삭제를 시도하는 회원
* @param comments 게시글에 포함된 댓글 목록
* @return 게시글을 삭제할 수 있다면 true 반환, 그렇지 않다면 false 반환
* @throws CannotDeletePostException 다른 회원이 작성한 게시글을 삭제할 수 없거나, 댓글이 존재하여 삭제할 수 없을 때 예외 발생
*/
public boolean canDelete(Member member, List<Comment> comments) {
    if (!member.isSameMemberId(this.memberId)) {
        throw new CannotDeletePostException(ErrorType.CAN_NOT_DELETE_OTHER_MEMBER_POST);
    }

    for (Comment comment : comments) {
        if (!comment.canDelete(member)) {
            throw new CannotDeletePostException(ErrorType.CAN_NOT_DELETE_POST_WITH_OTHER_MEMBER_COMMENTS);
        }
    }
    return true;
}
```

굳이 전체 코드를 읽지 않아도, 메서드 동작을 설명하는 내용만 봐도 해당 메서드가 어떤 동작을 수행하고 어떠한 값을 반환하는지 알 수 있다.

프로젝트를 진행하면서 이러한 주석은 거의 모든 메서드에 적어놓았다.

<br>

하지만, 메서드에 변경사항이 있을 때마다 주석을 최신 상태로 유지해야하는 번거로움이 있었다.
또, 주석을 수정하지 않아서, 실제 동작과 일치하지 않는 주석이 꽤 있었다.

즉, 잘못된 주석으로 인해 혼란을 야기할 수 있는 가능성이 존재하다는 것이 단점이 있었다.  

(*하지만.. 읽기 쉬운 코드로 만들기 위해서는 이만한 방법보다 더 좋은 방법이 있을까?*)

### 2. 역할과 책임이 명확하게 분리된 코드  

코드를 작성하다보면, 하나의 객체가 모든 일을 처리해서 복잡도가 증가하다고 생각되면 다른 객체에게 위임한다. 
이를 통해 역할과 책임을 명확하게 구분하는 편이다.

예를 들어보면,
현재 `Car`클래스에는 멤버 변수`name`과 `position`이 선언되어 있다.  

```
public class Car {
    private static final int MIN_FORWARD_VALUE = 4;
    private static final int MAX_NAME_LENGTH_VALUE = 5;
    private String name;
    private int position;

    public Car(String name) {
        this(name, 0);
    }

    public Car(String name, int position) {
        if( StringUtils.isBlanck(name) ) 
            throw new IllegalArgumentException("name은 1글자 이상을 입력해야 합니다.");
        if( isInvalidNameLegnth(name) )
            throw new IllegalArgumentException("name은 5글자를 초과할 수 없습니다.");
        if( position < 0 ) {
            throw new IllegalArgumentException("position을 음수로 지정할 수 없습니다.");
        }
        ...

        this.name = name;
        this.position = position;
    }
    // 생략..
```

`Car` 객체를 생성할 때, 각 멤버변수(필드)에 대한 유효성 체크를 진행하는 것을 볼 수 있다.  

대충 봤을 때는 `Car` 클래스의 복잡도는 그리 높진 않지만, 만약 요구사항이 추가되고 멤버 변수가 늘어나 100개 이상이 된다면 어떻게 될까?

이럴때는 각 역할과 책임을 분리한다.

```
public class Car {
    private static final int MIN_FORWARD_VALUE = 4;
    private Name name;
    private Position position;
    // 생략...
}

public class Position {
    private int position;

    public Position(int value) {
        if( value < 0 ) {
            throw new IllegalArgumentException("position을 음수로 지정할 수 없습니다.");
        }
        this.position = value;
    }
}
    
    // 생략...
public class Name {
    private static final int MAX_NAME_LENGTH_VALUE = 5;
    private String name;

    public Name(String name) {
        if( StringUtils.isBlanck(name) ) 
            throw new IllegalArgumentException("1글자 이상을 입력해야 합니다.");
        
        if( isInvalidNameLegnth(name) )
            throw new IllegalArgumentException("5글자를 초과할 수 없습니다.");
        this.name = name;
    } 
}
```

기존에 `Car` 클래스에 선언된 `position`과 `name`에 대한 유효성 체크 로직이 각각의 클래스로 이동한 것을 확인할 수 있다.

### 3. 테스트 가능한 코드

나는 코드를 작성하고나서, 항상 단위 테스트를 작성하는 편이다.

간혹, 테스트하기 어려운 코드는 발견되는데 이는 외부 환경에 의존하는 코드다.

예를 들면,
현재 시간에 따라, `퇴근` 혹은 `근무` 문자열을 반환하는 메서드가 있다.

```
public class StatusChecker {

    public String checkLeaveTime() {
        LocalDateTime now = LocalDateTime.now();
        int hour = now.getHour();

        if (hour >= 18) {
            return "퇴근";
        }
        return "근무";
    }
}
```

이에 대한 테스트는 다음과 같다.

```
@Test
void leave() {
    StatusChecker statusChecker = new StatusChecker();
    assertThat(statusChecker.checkLeaveTime()).isEqualTo("퇴근");
}

@Test
void work() {
    StatusChecker statusChecker = new StatusChecker();
    assertThat(statusChecker.checkLeaveTime()).isEqualTo("근무");
}
```

테스트를 실행하는 시점에 따라 테스트 메서드 중 하나는 무조건 실패하게 된다.

테스트는 기존 구현된 로직을 변경되지 않는 한 항상 동일한 결과가 나와야하는데...
기존 구현된 코드는 테스트가 가능한 코드일까?

아니다. 나는 이러한 코드를 테스트가 불가능한 코드라고 생각한다.

그렇다면, 테스트 가능한 코드로 리팩토링하려면 강하게 결합되어있는 의존관계를 느슨하게 바꿔주어야 한다.

```
public class StatusChecker {

    public String checkLeaveTime(int hour) {
        if (hour >= 18) {
            return "퇴근";
        }
        return "근무";
    }
}
```

```
@Test
void leave() {
    StatusChecker statusChecker = new StatusChecker();
    assertThat(statusChecker.checkLeaveTime(createHour(20))).isEqualTo("퇴근");
}

@Test
void work() {
    StatusChecker statusChecker = new StatusChecker();
    assertThat(statusChecker.checkLeaveTime(createHour(13))).isEqualTo("근무");
}

int createHour(int hour) {
    return LocalTime.of(hour, 0).getHour();
}
```  

<br>

이처럼 객체 간의 의존관계에 대한 결정권을, 의존관계를 가지는 객체가 가지는 것이 아닌 외부의 누군가 맡기는 편이다.

### 마무리

내가 생각하는 좋은 코드에 대해서 스스로 물어보고 대답한 것에 대해서 글로 정리해보았다.

나는 성격이 급하다보니 회고하는 습관이 정말 없다.
앞으로는 내가 고민한 내용에 대해서 깊게 고민해보고자 한다.

</div>