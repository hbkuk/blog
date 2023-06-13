<div class="markdown-body">

# Vue.js 구조 잡기

<p align="center">
  <img src="https://github.com/hbkuk/board-web-spring/assets/109803585/358c6352-e514-44f0-9381-56d793d981fe" alt="text" width="number" />
</p>  

<br>

## Vue 애플리케이션의 진입점  

### public>index.html은 Vue 애플리케이션의 진입점입니다.  

기본적인 **HTML 구조와 Vue 앱에 필요한 리소스를 로드**하는 **<u>스크립트 태그</u>를 포함**해야 합니다.  

예를 들면 다음과 같은 내용으로 구성될 수 있습니다.

```
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Vue App</title>
</head>
<body>
  <div id="app"></div> <!-- Vue 앱이 마운트될 위치 -->
  
  <!-- Vue 앱에 필요한 CSS 파일 -->
  <link rel="stylesheet" href="https://unpkg.com/bootstrap/dist/css/bootstrap.min.css">
  
  <!-- Vue 앱에 필요한 JavaScript 파일 -->
  <script src="https://unpkg.com/vue@2.6.14/dist/vue.min.js"></script>
  
  <!-- Vue 앱의 진입점 스크립트 파일 -->
  <script src="/dist/app.js"></script>
</body>
</html>
```  

<br>

## 재사용(재활용) 가능한 부분을 Component 분리  

만약 `Home.vue`에서 다음과 같은 코드가 있다고 가정해보겠습니다.

<p align="center">
  <img src="https://github.com/hbkuk/board-web-spring/assets/109803585/f548a48e-cea2-4afc-97f3-26a2f9a0198b" alt="text" width="number" />
</p>  

이러한 상황에서는 **`div class="col"`로 시작하는 부분을 컴포넌트화**할 수 있습니다.  

컴포넌트를 만들기 위해서 다음과 같은 절차로 진행될 수 있습니다.  

- `components` 디렉토리에 새로운 Vue 컴포넌트 파일 (예: `Card.vue`)을 생성합니다. 
- 해당 컴포넌트 파일에 중복되는 내용을 추가합니다.
```
// 예시
<template>
  <div class="col">
    <div class="card shadow-sm">
      <svg class="bd-placeholder-img card-img-top" width="100%" height="225" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Placeholder: Thumbnail" preserveAspectRatio="xMidYMid slice" focusable="false">
        <title>Placeholder</title>
        <rect width="100%" height="100%" fill="#55595c" />
        <text x="50%" y="50%" fill="#eceeef" dy=".3em">Thumbnail</text>
      </svg>

      <div class="card-body">
        <p class="card-text">This is a wider card with supporting text below as a natural lead-in to additional content. This content is a little bit longer.</p>
        <div class="d-flex justify-content-between align-items-center">
          <div class="btn-group">
            <button type="button" class="btn btn-sm btn-outline-secondary">View</button>
            <button type="button" class="btn btn-sm btn-outline-secondary">Edit</button>
          </div>
          <small class="text-muted">9 mins</small>
        </div>
      </div>
    </div>
  </div>
</template>
```
- 상위 혹은 다른 Vue 파일에서 아래와 같이 **import한 후 사용**합니다.  

```
<template>
  <div>
    <CardComponent />
  </div>
</template>

<script>
import CardComponent from '@/components/CardComponent.vue';

export default {
  components: {
    CardComponent,
  },
  // ...
}
</script>

```  

만약 **<u>상위 컴포넌트</u>**에서 **<u>하위 컴포넌트</u>로 데이터를 전달**하고 싶을 때는 어떻게 해야할까요?

<br>

## 데이터 바인딩(Data-Binding): 부모 컴포넌트에서 자식 컴포넌트로 데이터 전달

만약, **`Home.vue`에서 `Card.vue`**를 사용한다면, 다음과 같은 코드가 사용될 수 있습니다.  

아래 코드는 상위 컴포넌트인 `Home.vue`의 코드 일부입니다.

<p align="center">
  <img src="https://github.com/hbkuk/board-web-spring/assets/109803585/6f37e428-9aea-4daf-a6b2-210390d57bb0" alt="text" width="number" />
</p>  

- `:item="item"`은 item이라는 상위 컴포넌트의 데이터를 **Card 컴포넌트의 item 속성에 바인딩**한다는 의미입니다.
- **`v-for` 디렉티브**를 통해 `state.items` 배열 순회하면서 **item이라는 변수에 할당하고, item 속성으로 전달**하고 있습니다. 

<br>

그렇다면, **하위 컴포넌트는 순서대로 다음과 같은 Object를 전달**받습니다.  

```
[{
	"id": 1,
	"name": "blue",
	"imgPath": "/img/blue-flower-gbb4014f2a_1280.jpg",
	"price": 10000000,
	"discountPer": 5
}, {
	"id": 2,
	"name": "cat",
	"imgPath": "/img/cat-g405a9024b_1280.jpg",
	"price": 20000000,
	"discountPer": 10
}, {
	"id": 3,
	"name": "flowers",
	"imgPath": "/img/flowers-ge7bf4af11_1280.jpg",
	"price": 30000000,
	"discountPer": 30
}]

```

<br>

그렇다면, Card 컴포넌트에서는 어떻게 전달받아 사용하는지 확인해보겠습니다.  

<p align="center">
  <img src="https://github.com/hbkuk/board-web-spring/assets/109803585/3100e725-cc80-4aa7-8b57-a6006856bde8" alt="text" width="number" />
</p> 

Card 컴포넌트에서는 **`props`로 item을 정의**하여 해당 속성을 받을 수 있습니다.  
여기서, `props`는 부모 컴포넌트로부터 전달받은 속성을 사용할 수 있도록 하는 **Vue 컴포넌트의 기능**입니다.  

## Vue Router: URL 주소에 따른 페이지 관리  

<p align="center">
  <img src="https://github.com/hbkuk/board-web-spring/assets/109803585/ac6ff3cb-3949-4dac-afba-5ae04d36c8a9" alt="text" width="number" />
</p> 

- **router 배열을 정의**합니다. 이 배열은 라우팅 경로와 해당 경로에 대한 **컴포넌트를 매핑**합니다.  
- **`createRouter` 함수를 사용**하여 라우터 인스턴스를 생성
- **`createWebHistory`를 사용**하여 HTML5 History 모드의 라우터를 생성  

## Vue Router Push: 동적 라우팅 처리  

예를 들어, 아래와 같이 로그인이 성공한 후 특정 페이지로 이동하는 코드를 살펴보겠습니다.

<p align="center">
  <img src="https://github.com/hbkuk/board-web-spring/assets/109803585/285764ef-c416-49b7-82ab-db1956619715" alt="text" width="number" />
</p> 

- **`axios.post()` 함수를 통해 서버에 POST 요청**을 보냅니다. 요청 데이터는 `state.form` 입니다.
- **`router.push`** 함수를 통해 페이지를 **`/(홈 페이지)`로 전환**합니다.

</div>