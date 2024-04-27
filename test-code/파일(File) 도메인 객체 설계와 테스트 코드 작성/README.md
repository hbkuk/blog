<div class=markdown-body>  

#### [NOW](https://github.com/hbkuk/now-back-end) 프로젝트를 진행하면서 기록한 글입니다.

# 파일(File) 도메인 객체 설계와 테스트 코드 작성

**지난번 포스팅에서는 [게시글(POST) 도메인 모델링(Domain Modeling)을 진행](https://starting-coding.tistory.com/655)했었습니다.**

해당 글은 이전에 구현하지 못했던 **커뮤니티(Community), 사진(Photo) 게시글의 파일 업로드와 관련된 요구사항을 기반으로 도메인 모델링을 진행**하고자 합니다.

지난 번 포스팅에서 작성했던 내용입니다.

![지난 번의 요구사항](https://github.com/hbkuk/blog/assets/109803585/27573538-afed-4bed-bbd0-6f2beb46b4cd)

표시한 부분을 제외한 모든 내용은 지난 번 포스팅에서 어떻게 모델링했는지 설명드렸습니다.  

이번 포스팅은 표시한 파일 업로드에 대해서 **도메인 객체를 설계**하고, **테스트 코드 작성**을 하는 것까지의 과정을 소개해드리고자 합니다.  

<br>

## 도메인 모델링

파일 업로드와 관련된 요구사항 중 허용하는 **확장자**, **최대 파일 크기**, **최대 파일 개수**는 프론트에서 확인할 수 있겠지만, **최종적으로 백엔드(Server)에서 확인**해야 합니다.  

그 이유는 **악의적으로 요청을 조작하거나 우회할 수 있는 가능성이 있기 때문**입니다.  

<br>

그렇다면, 다음과 같이 **`File` 도메인 객체를 설계**할 수 있겠습니다.

```
public class File {

    /**
     * 파일의 고유 식별자
     */
    private final Long fileIdx;

    /**
     * 서버 디렉토리에 저장된 파일 이름
     */
    private final String savedFileName;

    /**
     * 사용자가 알고 있는 실제 파일 이름
     */
    private final String originalFileName;

    /**
     * 파일의 확장자명
     */
    private final String fileExtension;

    /**
     * 파일의 크기
     */
    private final int fileSize;

    /**
     *  게시글의 고유 식별자
     */
    private Long postIdx;
}
```

그렇다면, <u>**유효성 검증 로직**</u>은 어디다 두어야 할까요?  

<br>

아래와 같이 **`FileValidationUtils` 클래스를 정의해두는 것도 좋은 방법**일 수 있습니다.  

```
public class FileValidationUtils {

    private static final String FILE_NAME_EXTENSION_REGEX = "\\.(\\w+)$";
    private static final Pattern EXTENSION_PATTERN_COMPILE = Pattern.compile(FILE_NAME_EXTENSION__REGEX);

    public static void validateOnCreate(File file) {
        log.debug("validateOnCreate... 유효성 검증 -> file : {}", file);

        validateFileName(file.getOriginalFileName());
        validateFileSize(file.getFileSize());
        ...
    }

    private static void validateFileName(String fileName) {
        if (isInvalidImageName(fileName)) {
            throw new IllegalArgumentException("유효하지 않은 확장자입니다.");
        }
        if (!isValidSize(fileName, MIN_FILE_NAME_VALUE, MAX_FILE_NAME_VALUE)) {
            throw new IllegalArgumentException("파일 이름은 ...");
        }
    }

...
}
```  

필요할떄 마다, 다음과 같이 사용할 수 있습니다.

```
public void createFile(File file) {
    FileValidationUtils.validateOnCreate(file);
    // 로직 ..
}
```  

<br>

하지만, 저는 이 부분에 대해서 조금 생각이 다른데요,

그 이유는, **유효성 검증 로직은 도메인 객체에서 진행**되어야 하며, "**책임은 도메인 객체 자신에게 있다.**" 라고 생각하기 떄문입니다.  

<br>

### 유효성 검증의 책임은 도메인 객체 자신에게 있다?  

**유효성 검증을 해당 도메인 객체에서 진행**되어야 하고,

해당 **도메인 객체에서 책임을 갖고** 유효성 검사를 처리한 후에, **필요로 하는 객체로 전달**함으로써,

**수많은 도메인 객체를 사용하는 환경에서 문제가 발생할 여지를 최소화** 될 수 있다고 생각합니다.  

따라서, 다음과 같이 **유효성 검증 로직을 `File` 도메인 객체 생성자에 위치**시켰습니다.

```
public File(Long fileIdx, String savedFileName, String originalFileName, String fileExtension, int fileSize, Long postIdx,
            List<String> allowedExtensions, int maxFileSize) {

    if (originalFileName.length() > 500) {
        throw new IllegalArgumentException("파일 이름은 500자를 초과할 수 없습니다.");
    }

    if(!allowedExtensions.contains(fileExtension)) {
        throw new IllegalArgumentException("허용하지 않는 확장자입니다.");
    }

    if (fileSize > maxFileSize) {
        throw new IllegalArgumentException("허용하지 않는 파일 크기입니다.");
    }

    this.fileIdx = fileIdx;
    this.savedFileName = savedFileName;
    this.originalFileName = originalFileName;
    this.fileExtension = fileExtension;
    this.fileSize = fileSize;
    this.postIdx = postIdx;
}
```  

하지만, 현재보다 **요구사항이 더 늘어나서, 검증해야할 항목이 많아진다면** 어떻게 해야할까요?

그러한 상황을 **미리 대비해서, 지금.. 또 다른 객체로 분리**해야합니다.  

<br>

### 원시값 포장(Wrapping) 객체  

![원시값 포장 객체](https://github.com/hbkuk/blog/assets/109803585/195da05f-6e12-43ca-a5fc-510b6ae72c85)

필드의 **데이터 타입이 해당 필드의 이름으로 변경**된 것을 확인하셨나요?  

**원시값을 포장한 객체를 만들어서 해당 객체 내에서 생성될때 유효성 검사가 진행되도록 위임**했습니다.  

아래 코드를 보시면 이해하실 수 있으실 겁니다.

<br>

```
/**
 * 원본 파일 이름을 나타내는 원시값 포장 객체
 */
public class OriginalFileName {
    private static final int MAX_FILE_NAME_LENGTH = 500;
    private final String originalFileName;

    /**
     * OriginalName 객체 생성
     *
     * @param fileName 파일 이름
     * @throws IllegalArgumentException 파일 이름이 정해진 길이를 초과할 경우 예외를 발생시킴
     */
    public OriginalFileName(String fileName) {
        if (fileName.length() > MAX_FILE_NAME_LENGTH) {
            throw new IllegalArgumentException("파일 이름은 500자를 초과할 수 없습니다.");
        }
        this.originalFileName = fileName;
    }
}

/**
 * 파일 크기를 나타내는 원시값 포장 객체
 */
public class FileSize {
    private final int fileSize;

    /**
     * FileSize 객체를 생성
     *
     * @param fileSize       파일 크기 값
     * @param maxFileSize  허용되는 최대 파일 크기
     * @throws IllegalArgumentException 파일 크기가 허용된 크기를 초과할 경우 발생하는 예외
     */
    public FileSize(int fileSize, int maxFileSize) {
        if (fileSize > maxFileSize) {
            throw new IllegalArgumentException("허용하지 않는 파일 크기입니다.");
        }
        this.fileSize = fileSize;
    }
}

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

원시값을 포장한 객체로 유효성 검사를 위임하니, 다음과 같은 **테스트가 가능**해졌습니다.  

테스트 코드를 작성해보겠습니다.  

여기서는 **파일 확장자를 나타내는 원시값 포장 객체**와 **파일 크기를 나타내는 원시값 포장 객체**에 대해서만 테스트 해보겠습니다.  

#### FileExtensionTest.java
![확장자 관련 테스트 코드](https://github.com/hbkuk/blog/assets/109803585/74a7bbcd-c5a5-4109-abbf-c3706a0ce503)

#### FileSizeTest.java
![사이즈 관련 테스트 코드](https://github.com/hbkuk/blog/assets/109803585/70262f89-e1e9-4cf6-a5ae-bd36ec15d53b)  

결과적으로, 
**원시값 포장(Wrapping) 객체**를 사용하여 **파일 이름, 파일 크기, 파일 확장자와 같은 필드**에 대한 **유효성 검증을 캡슐화**했습니다.  

앞으로도 필자는 이러한 방식으로 **도메인 객체를 설계하고자 합니다.**  

다음 포스팅에서는 해당 **도메인 객체를 어떻게 사용하고 있는지에 대해서 소개**해 드리겠습니다.  

이상 마치겠습니다. 감사합니다.

</div>