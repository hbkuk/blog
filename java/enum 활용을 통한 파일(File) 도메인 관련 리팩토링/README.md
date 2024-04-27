<div class=markdown-body>  

#### [NOW](https://github.com/hbkuk/now-back-end) 프로젝트를 진행하면서 기록한 글입니다.

#### 이전 포스팅
- [게시글(POST) 도메인 모델링(Domain Modeling)](https://starting-coding.tistory.com/655)
- [파일(File) 도메인 모델링(Domain Modeling)](https://starting-coding.tistory.com/657)  

이전 파일 도메인 모델링에서.. 

**원시값 포장(Wrapping) 객체**를 사용하여 **파일 이름, 파일 크기, 파일 확장자와 같은 필드**에 대한 **유효성 검증 로직을 캡슐화**했습니다.  

이번 포스팅에서는 **파일 도메인 객체를 어떻게 사용하고 있는지**와, **`ENUM`을 활용한 리팩토링 사례**에 대해서 소개해 드리고자 합니다.  

<br>

본격적인 설명에 들어가기에 앞서,  

현재 진행중인 **[NOW](https://github.com/hbkuk/now-back-end) 프로젝트에 대해서 간략하게 소개**해 드리겠습니다.

- 스프링 부트 버전: **2.6.3**
- 자바 버전: **11**
- **토큰(JWT) 기반 인증 방식**
- 파일 업로드를 위한 **`MultipartFile` 라이브러리 적용**
- 응답이 `JSON` 형태인 **`RESTful API` 방식**

해당 포스팅에서는 **`토큰(JWT) 기반 인증 방식`에 대해서는 제외해서 설명**해보도록 하겠습니다.  

### 게시글을 저장 후 파일 업로드 및 저장까지의 흐름

**파일 업로드와 관련된 요구사항을 다시한번 확인**해보겠습니다.  

![지난 번의 요구사항](https://github.com/hbkuk/blog/assets/109803585/27573538-afed-4bed-bbd0-6f2beb46b4cd)  

<br>

위 내용을 확인하셨다면, 

요구사항에 따른 **커뮤니티 혹은 사진 게시글 저장 후 파일 업로드 및 저장까지의 흐름**을 살펴보도록 하겠습니다.

#### 1) 게시글 저장
- 클라이언트는 **`POST` 요청을 통해 게시글 저장 요청**
- 해당 요청은 **`PostController`의 핸들러 메서드로 전달**
- `PostService`에서는 받은 요청을 처리하여 **게시글을 데이터베이스에 저장**  
#### 2) 파일 업로드 및 저장
- 파일 업로드를 위해 **`FileService`를 호출**
- `FileService`는 **`MultipartFile` 객체를 순회하면서 서버 디렉토리에 업로드**(**서버 디렉토리 업로드는 FileUtils 클래스에 책임 위임**)
- 서버 디렉토리에 저장한 파일 내용을 기반으로 **파일을 데이터베이스에 저장**

<br>  

흐름을 이해하시기 어려우셨다면, **`PostController` 코드를 보면 이해하기가 수월하실거라 생각합니다.**  

![컨트롤러 핸들러 메서드](https://github.com/hbkuk/blog/assets/109803585/455b0584-6f81-43fc-8213-5c1f4f0d6711)  

<br>

만약, **[Postman(포스트맨)](https://www.postman.com/)으로 커뮤니티 게시글 저장 요청**을 한다면 다음과 같은 형식이 될겁니다.  

![포스트맨 요청](https://github.com/hbkuk/blog/assets/109803585/a9b1ffce-3df2-415d-902e-8c5e5680cdad)  

<br>

다시 본론으로 돌아와서, 위 컨트롤러의 코드에서 무언가 **나쁜 냄새(Bad Smell)** 가 납니다.  

그 부분은 **`fileService` 에게 인자로 전달하는 부분**인데요. 이 부분을 바로.. **`ENUM`을 통해서 개선한 사례**로 알려드리고자 합니다.  

우선, 코드의 흐름만 먼저 이해하시면 됩니다.  

<br>

다음은 **`fileService`의 코드입니다.**  

![컨트롤러 핸들러 메서드](https://github.com/hbkuk/blog/assets/109803585/8453e86b-ee13-406a-944f-4463e0338118)  

지난번 포스팅에서 **원시값 포장(Wrapping) 객체를 사용하여 유효성 검증을 캡슐화** 했습니다.  

위 사진에서 **`converToFile` 메서드에 대해서는 아래 코드**를 보시겠습니다.  

![파일 객체 변환 로직](https://github.com/hbkuk/blog/assets/109803585/20a14327-c89f-49e2-990d-473f047947c3)  

지난번 포스팅에서 **`File` 도메인 객체 모델링**했을때, 아래와 같이 **원시값을 포장한 객체에서는 생성될때 유효성 검사가 진행되도록 위임**했었습니다.  

아래와 같은 코드로요. 


```
/**
 * 파일 확장자를 나타내는 원시값 포장 객체
 */
public class FileExtension {
    private final String fileExtension;

    /**
     * Extension 객체 생성
     *
     * @param extension     파일 확장자
     * @param allowedExtensions 허용되는 확장자 그룹
     * @throws IllegalArgumentException 허용되지 않는 확장자일 경우 예외를 발생시킴
     */
    public FileExtension(String extension, List<String> allowedExtensions) {

        if(!allowedExtensions.contains(extension)) {
            throw new IllegalArgumentException("허용하지 않는 확장자입니다.");
        }
        this.fileExtension = extension;
    }
}
```  

<br>

자, 여기까지 충분히 이해하셨을거라 생각됩니다.  

위 코드에서 **나쁜 냄새(Bad Smell)** 가 나는 코드를 리팩토링해보겠습니다.  


### 인터페이스 활용  

**인터페이스 상수는 인터페이스 내에 선언된 필드**이며, 기본적으로 **`public static final`로 선언**됩니다.  
**고정된 값 혹은 수정이 불가능하게 막기 위해서 많이 사용**됩니다.

따라서, **인터페이스 상수를 통해 리팩토링을 진행** 했습니다.

```
public interface UPLOAD {

    List<String> allowedFileUploadExtensions = List.of("jpg", "gif", "png", "zip");
    int maxFileUploadSize = 2048000;
    int maxFileUploadCount = 5;

    List<String> allowedImageUploadExtensions = List.of("jpg", "gif", "png");
    int maxImageUploadSize = 1024000;
    int maxImageUploadCount = 20;
}
```

**`UPLOAD` 인터페이스를 활용한 테스트를 진행**했습니다.  

![개선한 테스트 코드](https://github.com/hbkuk/blog/assets/109803585/e5158f41-a8a5-4f24-a201-9061b458d5c4) 

모든 테스트는 성공합니다. 

![테스트 성공](https://github.com/hbkuk/blog/assets/109803585/2cea4476-0ab8-4a31-8ad8-cef84a867d96)  

<br>  

위처럼 인터페이스 상수를 선엄 함으로써, **추후 변경이 있을때는 인터페이스의 값만 변경**하면 됩니다.  

<br>

하지만 여기서 문제가 있습니다.  

해당 인터페이스를 통해 해결했던 개발자만 안다는 것인데요.

예를 들어, 해당 **시스템에 대해서 완벽하게 알지 못하는 개발**자가
- 이 내용을 알까요?
- **확장자 목록을 직접 생성 후 입력**한다면요?  

<br>

또한, 현재 **`fileService`의 insert 메서드는 여러개의 인자**를 받고 있습니다.  
```
fileService.insert(multipartFiles, community.getPostIdx(), ALLOWED_FILE_UPLOAD_EXTENSIONS, MAX_UPLOAD_SIZE, MAX_UPLOAD_COUNT);
```  
<br>

IDE의 지원을 받으면 쉬울 수 있지만, IDE의 지원을 받지 못하는 최악의 경우를 가정해보면.. 
- **인자의 순서와 타입을 정확히 입력**할 수 있을까요?
- **인자의 개수가 많을수록 메서드의 사용법을 이해하기 쉬울까요?**  

**특정 인자를 생략하거나 잘못된 인자를 전달하는 실수가 발생할 수 있습니다.**


이 문제를 해결할 수 있는 것은 **`eunm`** 입니다.(해당 포스팅에서는 enum에 대한 설명은 별도로 하지 않겠습니다.)  


### enum으로 변경

```
/**
 * 파일 업로드 타입을 나타내는 enum
 */
public enum UploadType {
    FILE(List.of("jpg", "gif", "png", "zip"), 2048000, 5),
    IMAGE(List.of("jpg", "gif", "png"), 1024000, 20);

    private final List<String> allowedExtensions;
    private final int maxUploadSize;
    private final int maxUploadCount;

    /**
     * UploadType 객체를 초기화하는 생성자
     *
     * @param allowedExtensions 허용하는 파일 확장자 목록
     * @param maxUploadSize 파일의 최대 업로드 크기 (바이트 단위)
     * @param maxUploadCount 최대 업로드 횟수
     */
    UploadType(List<String> allowedExtensions, int maxUploadSize, int maxUploadCount) {
        this.allowedExtensions = allowedExtensions;
        this.maxUploadSize = maxUploadSize;
        this.maxUploadCount = maxUploadCount;
    }

    public List<String> getAllowedExtensions() {
        return allowedExtensions;
    }

    public int getMaxUploadSize() {
        return maxUploadSize;
    }

    public int getMaxUploadCount() {
        return maxUploadCount;
    }
}
```  
위처럼 **서로 관련 있는 상수를 논리적으로 그룹화**했습니다.

또한, 아래와 같이 사용가능합니다.

![enum 활용](https://github.com/hbkuk/blog/assets/109803585/0be46f18-181f-41e4-a133-cf85fcdab6b5)  

여기까지 진행했다면,  

해당 시스템에 대해서 완벽하게 알지 못하는 개발자도 허용하는 확장자를 직접 생성 후 입력하는 경우는 없을 것이라고 생각됩니다.  

정말 부족한 예제이지만, 제가 어떻게 테스트 코드를 미리 작성하고 리팩토링하는 과정을 겪었는지에 대해서 조금이나마 이해가 되셨다면 좋겠습니다.   

이상 마치겠습니다. 긴 글을 읽어주셔서 진심으로 감사드립니다.  



</div>