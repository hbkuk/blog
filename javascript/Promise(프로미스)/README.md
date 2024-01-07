<div class=markdown-body>

## Promise(프로미스)

### Promise란 무엇일까요?
비동기 작업을 수행하는 함수의 **`Return` 타입**이라고 볼 수 있습니다.

이에, 대표적으로 네트워크 요청을 만들고 응답을 처리하는데 사용하는 `fetch` 함수가 있습니다.  

예를 들면, 아래와 같이 사용합니다.

```
fetch('https://api.example.com/data')
  .then(response => {
    if (!response.ok) { // 네트워크 요청이 성공
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log(data); // 처리된 데이터를 사용
  })
  .catch(error => {
    console.error('Fetch error:', error); // 네트워크 요청이 실패
  });

```

요청을 만들고, 응답을 처리하는데 있어서 불가피하게 **delay가 발생**할 수 밖에 없습니다.  

따라서, `fetch` 함수를 포함한, 비동기 작업을 수행하는 함수들은 **`Promise` 객체를 반환**합니다.   
이에, `Promise` 객체는 다음 작업이 순차적으로 실행될 수 있도록 `then`, `catch` 함수를 제공합니다.

**왜 `Promise` 객체를 반환하게 되었을까요?**  

처음부터 `Promise` 객체를 반환하는 것이 표준이었을까요?

### 꼭 Promise이어야만 했을까요?

`Promise`가 표준이 된 것은 ES6 시점입니다.<small>ES6란 2015년에 도입된 최신 버전의 JavaScript 입니다.</small>

`Promise`가 표준이 되기 전에는 비동기 코드를 다루기 위해 다양한 패턴과 라이브러리로 비동기 작업을 처리 했었습니다.  

이 말을 쉽게 풀어보자면, 주위 개발자가 작성한 비동기 작업 코드를 이해하기 위해서 라이브러리를 모두 공부해야만 했다면,
얼마나 피곤하고, 비효율적이었을까요?

한가지 예로, 콜백(callback) 패턴이 있습니다.  
함수 호출 시 매개변수로 성공했을 때 호출할 `onSuccess` 함수, 실패했을 때 호출할 `onError` 함수를 전달받아서 사용했다고 합니다. 
```
function doSomethingAsync(onSuccess, onError) {
    // 1. 어떠한 비동기적 작업 수행
    setTimeout(() => {
        const isSuccess = Math.random() > 0.5; // 무작위로 성공 또는 실패 결정

        // 2. 결과에 따라, onSuccess 혹은 onError 함수 호출
        if (isSuccess) {
            onSuccess('작업 성공!');
        } else {
            onError('작업 실패!');
        }
    }, 1000); // 예시로 1초 후에 작업이 완료되었다고 가정
}

// 함수 호출
doSomethingAsync(
    result => {
        console.log('성공 메시지:', result);
    },
    error => {
        console.error('에러 메시지:', error);
    }
);

console.log('비동기 작업이 완료되기를 기다리는 중...');
```  

간단한 방법이긴 하지만, 콜백 헬(Callback Hell)이 발생하기 쉬웠습니다.  
이로인해, 코드의 가독성이 저하되고 유지보수가 어려워지는 단점이 생겼습니다.

이를 해결하기 위해 표준으로 나온 것이 `Promise` 이며, 결과적으로 비동기 함수의 인터페이스를 통일했다고 볼 수 있습니다.

만약, 앞서 살펴봤던 함수를 `Promise`로 만든다면 어떻게 하면 될까요?  
아래 사진을 한번 보겠습니다.  

![비동기 작업 함수를 Promise로](https://github.com/hbkuk/blog/assets/109803585/b8f8c337-4671-4c25-a020-407b8056aa6e)

결론은, `Promise`로 감싸서 반환하면 됩니다.  

달라진 점은, 함수를 호출할 때, Callback 함수를 미리 받았어야 했었는데요.
이제는 그렇게 하지 않아도 된다는 것입니다.

단지, 이를 사용하는 개발자는 `Promise` 객체가 반환되구나 라고 생각하면 됩니다.

### 사용법은 어떻게 될까요?

![Promise 사용법](https://github.com/hbkuk/blog/assets/109803585/b85fbe1c-9f5c-4e0b-8cc7-3670af431055)

이전에는 작업이 완료된 후 실행할 Callback 함수를 매개변수로 전달했어야 했습니다.    

이에 반해, `Promise`는 `then`, `catch` 함수를 지원합니다.

따라서, 위 코드에서는 비동기 작업이 성공했을 때 호출할 `onSuccess` 함수를, 실패했을 때 호출할`onError` 함수를 인자로 전달하고 있습니다.  

<br>

만약, 여러 개의 비동기 작업들이 순차적으로 진행되어야 한다면 어떻게 하면 될까요?

`Promise`에서 제공하는 `then` 함수는 새로운 Promise 객체를 반환합니다.

그렇기 떄문에, 다음과 같이 코드를 작성할 수 있는데요.

![프로미스체이닝](https://github.com/hbkuk/blog/assets/109803585/917dedd8-ce7d-491b-b09c-b6e80c8b80e3)

`then` 메서드를 호출하면, 반환된 `Promise` 객체가 다음 `then` 함수로 전달됩니다.

하지만, 한가지 고민이 생기는데요.  

위와 같은 코드를 우리가 주로 많이 사용하는 패턴.. 동기적으로 작성할 순 없을까요?

이때, 나온 개념이 `Async/Await` 입니다.  

잠깐 비교해보자면...

<img width="584" alt="Promise와AsyncAwait비교" src="https://github.com/hbkuk/blog/assets/109803585/9cdc8100-c609-424a-889e-c55b5ea00682">

이에 대해서는, 다음 포스팅에서 작성해보겠습니다.

긴글 읽어주셔서 감사드립니다.

</div>