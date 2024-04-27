<div class=markdown-body>

# ENUM 활용한 Refactoring - 파일 확장자에 대한 유효성 검사는 어떻게 할까?  

##### > 현재 게시판을 주제로 한 프로젝트를 진행 중에 있습니다.  

해당 게시판에서 파일의 **업로드 개수는 최대 3개까지 가능**합니다.  

<p align="center">
  <img src="https://github.com/hbkuk/board-web/assets/109803585/175e75d2-78f2-4f2d-95c3-a205e328e197" alt="text" width="number" />
</p>   

파일 확장자에 대한 유효성 검사를 진행한다고 가정해봅시다.  

**업로드 가능한 파일의 확장자**는 다음과 같습니다.  

- png, jpeg, bmp, gif, jpg, docs  

<br>  

이러한 요구사항이 있을때, 어떻게 유효성 검사를 하면 좋을지 고민해보았습니다.  

다음과 같이 설계한 `File` 이라는 **도메인 객체에서 유효성 검증을 진행**했습니다.  

```
public class File {
    private final long FileIdx;
    private final String FileName;
    private final long FileSize;

    (빌더 패턴 관련 코드)...

    public File build() {
        List<String> extensions = Arrays.asList("PNG", "JPEG", "BMP", "GIF", "JPG");

        Pattern pattern = Pattern.compile("\\.(\\w+)$");
        Matcher matcher = pattern.matcher(fileName);

        if (!matcher.find()) {
            throw new IllegalArgumentException("유효한 파일이 아닙니다.");
        }

        String extension = matcher.group(1).toUpperCase();

        if (!extensions.contains(extension)) {
            throw new IllegalArgumentException("유효하지 않은 확장자입니다.");
        }

        if (fileSize >= 10_485_760) {
            throw new IllegalArgumentException("이미지의 크기가 10_485_760 byte 이상일 수 없습니다.");
        }

        return new File(this);
    }
}

```  

객체 생성될 때, 다음과 같은 로직으로 검사하며 아래와 같은 테스트 코드를 작성했습니다.  

```
@DisplayName("파일의 ")
public class FileTest {

    @Nested
    @DisplayName("이름은 ")
    class name {

        @DisplayName("유효한(png, jpeg, bmp 등) 확장자여야만 한다.")
        @ParameterizedTest
        @ValueSource(strings = {"test.png", "test.jpeg", "test.bmp", "test.gif", "test.jpg"})
        void valid_image_name_extension(String nameExtension) {
            File file = new File.Builder()
                    .FileName(nameExtension)
                    .fileSize(127904)
                    .build();
        }

        @DisplayName("유효하지 않은 확장자일 경우 예외가 발생한다.")
        @ParameterizedTest
        @ValueSource(strings = {"test.exe", "test.com", "test.bat", "test.ti", "test.abc"})
        void invalid_image_name_extension(String nameExtension) {
            assertThatExceptionOfType(IllegalArgumentException.class)
                    .isThrownBy(() -> {
                        new File.Builder()
                                .FileName(nameExtension)
                                .fileSize(127904)
                                .build();
                    })
                    .withMessageMatching("유효하지 않은 확장자입니다.");
        }
    }
}

```  

다음과 같이 테스트는 성공합니다.  

<p align="center">
  <img src="https://github.com/hbkuk/board-web/assets/109803585/e02cd555-da83-41d3-b585-c98d13346e1f" alt="text" width="number" />
</p>   

테스트 코드가 있으니, **점진적인 리팩토링이 가능**합니다.  

먼저 확장자 리스트는 도메인 객체인 **`File`의 생성자에서 `extensions` 이라는 지역변수로 다음과 같이 선언**되었습니다.  


```
List<String> extensions = Arrays.asList("PNG", "JPEG", "BMP", "GIF", "JPG");
```  

<br>

시스템이 확장되었을때를 생각하면서...

코드의 **가독성을 높이고 수정을 용이**하게 하게 하려면 어떻게 해야할까요?  

또, 도메인 **객체 내 전역에서 사용하게 된다면** 어떻게 해야할까요?  

<br>

그렇다면, 다음과 같이 **static(정적변수)으로 선언해주면서 리팩토링**을 할 수 있습니다.  

```
public class File {
    private static final List<String> EXTENSIONS = Arrays.asList("PNG", "JPEG", "BMP", "GIF", "JPG");
    
    private final long FileIdx;
    private final String FileName;
    private final long FileSize;
```  

<br>

여기서 또 한번 리팩토링을 할 수 있습니다.  

바로 **열거형(enum)을 사용한 리팩토링**입니다.  

<br>

## 열거형(enum) 이란?

`열거형(enum)`은 여러 상수로 이루어진 **고정 집합을 나타내는 특수 데이터 타입**이라고 할 수 있습니다.  

더 정확하게 말하면 자바 클래스의 특별한 한 종류라고 말할 수 있습니다. 보통 열거형은 아래와 같이 선언합니다.  

```
enum 이름 {
	상수1, 상수2, ..., 상수N
}

```  

열거형을 사용하면 **서로 관련 있는 상수를 논리적으로 그룹화**할 수 있습니다.  

예를 들어서 **방위(동, 서, 남, 북)를 나타내려면 열거형**을 아래와 같이 쓸 수 있습니다.

```
enum CardinalDirection {
	EAST, WEST, SOUTH, NORTH
}
```  

이를 프로젝트에 적용해보겠습니다.  

<br>

## 파일 확장자를 enum으로 그룹화 시키자.   

<p align="center">
  <img src="https://github.com/hbkuk/board-web/assets/109803585/c9fb4e11-61d7-461e-b626-9eadf8f3c8b8" />
</p>   

위와 같이 enum으로 그룹화 한다면 다음과 같은 장점이 있습니다.  

<br>

enum 을 사용하면 **파일 이름 확장자를 잘못 입력하는 것을 방지**할 수 있습니다.  

enum 의 값은 고정되어 있으므로 **코드에서 잘못된 파일 이름 확장자를 입력할 수 없습니다.**   

<br>

또한, 확장자를 쉽게 추가, 제거 또는 변경할 수 있습니다.  

enum 은 클래스와 달리 값이 고정되어 있지 않으므로 코드에서 **파일 확장자를 쉽게 변경**할 수 있습니다. 이로 인해 코드가 더 유연하고 확장 가능합니다.  


또한, `contains()`라는 메서드를 제공합니다.  
이 메서드는 확장자 문자열을 입력으로 사용하고 열거형에 확장자가 있는지 여부를 나타내는 boolean 값을 반환합니다.  

<br>

## File 도메인 객체에서의 점진적인 리팩토링  

```
public class File {
    private final FileIdx fileIdx;
    private final FileName fileName;
    private final FileSize fileSize; 
...


public class FileName {
    private static final String FILE_NAME_EXTENSION__REGEX = "\\.(\\w+)$";
    private static final Pattern EXTENSION_PATTERN_COMPILE = Pattern.compile(IMAGE_NAME_EXTENSION__REGEX);
    private String fileName;

    public FileName(String fileName) {

        if (isInvalidFileName(fileName)) {
            throw new IllegalArgumentException("유효하지 않은 확장자입니다.");
        }

        this.fileName = fileName;
    }

    private boolean isInvalidFileName(String fileName) {
        Matcher matcher = getMatcher(fileName);
        if (!matcher.find()) {
            return true;
        }
        if (!FileNameExtension.contains(matcher.group(1).toUpperCase())) {
            return true;
        }
        return false;
    }

    private Matcher getMatcher(String fileName) {
        return EXTENSION_PATTERN_COMPILE.matcher(fileName);
    }
}
```
</div>