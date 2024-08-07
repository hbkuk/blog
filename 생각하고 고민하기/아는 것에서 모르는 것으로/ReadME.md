# 아는 것에서 모르는 것으로

난관에 부딪혔을 때, `Kent Beck` 님의 명언을 통해 문제를 해결한 경험이 있습니다.  

> 사실은 상향식, 하향식 둘 다 TDD의 프로세스를 효과적으로 설명해 줄 수 없다. ...   
> 만약 어떤 방향성을 가질 필요가 있다면 '아는 것에서 모르는 것으로(Known-to-unknown)' 방향이 유용할 것이다.  
> 우리가 어느 정도의 지식과 경험을 가지고 시작한다는 점, 개발하는 중에 새로운 것을 배우게 될 것임을 예상한다는 점 등을 암시한다.
>
> Test-Driven Development, Kent Beck  

<br>


### TDD의 방향성 결정

저는 [ATTD, 클린 코드 with Spring 8기](https://edu.nextstep.camp/c/R89PYi5H)에 참여했었고, 미션을 진행했었어요.    

미션의 주요 내용으로는 인수 테스트를 작성하고 기능을 구현하기 전에,  
TDD의 방향을 `OutSide-In`으로 할 것인지 `Inside-Out`으로 할 것인지에 대해서 결정을 해야만 했었어요.  

![TDD 방향](https://github.com/hbkuk/blog/assets/109803585/7579fc70-d442-475d-a408-e88917a07a4d)

TDD의 방향에 대해서 고민하고, 결정을 해야했지만    
처음 접하는 도메인이었기 때문에 전체적인 비즈니스 요구사항에 대한 이해도가 너무나도 부족한 상황이었어요.

### 아는 것에서 모르는 것으로

어떠한 협력 객체들이 어떠한 협력을 해서 비즈니스 요구사항을 만족할 수 있는지? ...  
도무지 감이 잡히질 않았었습니다.  

이때, 저는 `Kent Beck`의 명언을 적용해보려고 시도해보았어요.  

현재 상황에서 제가 할 수 있는 것들을 하나씩 적어보았고, 그 중 협력 객체들 간의 의사소통을 위한 적절한 인터페이스를 정의를 했었습니다.

작성하고 나니, 협력 객체 간의 어떤 협력으로 기능이 작동하는지에 대한 큰 그림을 그릴 수 있었어요.    
요구 사항에 대해서 깊이 있게 이해하진 않았지만, 큰 그림을 기반으로 테스트를 작성하기로 결정했었어요.  
그러다보니, 모든 요구사항에 만족하는 테스트 코드와 기능을 구현할 수 있었어요.  

결국 TDD의 방향을 `OutSide-In`으로 진행한거더라구요. ㅎㅎ;;


### 사내에서 경험했던 것

또 다른 상황으로, 업무 전환이 발생하면서 운영 업무를 담당하게 되었을 때, 경험했던 내용이에요.    
코드를 분석하지 않은 프로젝트에서 버그 수정과 관련된 업무를 맡게 되었는데, 이때도 `Kent Beck` 님의 명언이 큰 도움이 되었습니다.


어떠한 버그인지 확인해보니, 특정 모바일 환경에서 `pdf` 다운이 안되는 것이었습니다.  
아직 코드 분석도 하지 않았는데, 어디서부터 시작해야 할지... 정말 막막했었습니다.


이때 저는,  
문제를 해결하기 위한 접근 방식으로 제가 뭘 할 수있고, 뭘 할 수 없는지에 대해서 간략하게 나열했었어요.  

#### 할 수 있는 것
- 다운로드 버튼까지 진입할 수 있는 경로
- 코드 분석
- 회사 내 자원(동일하지 않은 환경)으로 테스트
- ...

#### 할 수 없는 것
- 테스트 계정
- 모바일 환경 구축
- ...

이를 통해 어디서부터 시작해야 할지에 대한 방향성을 잡을 수 있었어요.    
또한, 할 수 없는 것에 대해서 동료 개발자분들에게 공유를 했고, 이에 대한 도움을 받을 수 있었습니다.