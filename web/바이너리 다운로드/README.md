<div class="markdown-body">  

## Java를 사용한 바이너리(binary) 파일을 다운로드하는 프로세스  

<p align="center">
  <img src="https://github.com/hbkuk/blog/assets/109803585/181238d2-236d-4bce-b703-c2d3aec6b621" alt="text" width="number" />
</p>    

**사용자가 파일을 업로드** 하게되면,  

**서버에서는 사용자가 해당 파일을 다운로드를 할 수 있게 다운로드 기능을 제공**할 수 있습니다.  

<br> 

이를, 서버의 파일 디렉토리에서 **바이너리 파일을 읽은 다음** 클라이언트의 **웹 브라우저로 전송**함으로써, 구현할 수 있습니다.  

<br>

구현하기 위해서는 다음과 같은 절차로 진행되어야 합니다.  

- **파일 객체 생성**
- **사용자 에이전트 확인**
- **응답 헤더 설정**
- **요청 브라우저에 따른 파일 이름 인코딩**
- **콘텐츠 길이 설정**
- **바이너리 데이터 읽기 및 쓰기**

---

### 파일 객체 생성  

```
InputStream in = null;
File file = null;
boolean skip = false;

try {
    file = new File(UPLOAD_PATH, savedFileName);
    in = new FileInputStream(file);
} catch (FileNotFoundException fe) {
    skip = true;
}
``` 

다운로드를 제공할 **`File` 객체를 생성하는 것**으로 시작합니다.  

이는 **파일의 존재를 확인하고 길이를 얻는 데 사용**됩니다.  

또한, 파일의 내용을 읽는 데 사용할 수 있는 **입력 스트림(in)이 생성**합니다.  

`FileInputStream` 생성 중 **FileNotFoundException**이 발생하면 지정된 파일이 존재하지 않는다는 의미입니다.  

<br>

### 사용자 에이전트 확인

```
client = request.getHeader("User-Agent");
```  

`User-Agent` HTTP 헤더는 클라이언트가 요청한 **웹 브라우저에 대한 정보를 제공**합니다.  

이를 통해, **클라이언트의 브라우저 유형에 따라 호환성을 보장**하기 위함입니다.  

<br>

예를 들면,

Chrome 브라우저와 정상적으로 출력되지만,  **IE에서는 인코딩 방식이 다르기 때문에 한글 이름이 제대로 출력되지 않습니다.**  
 
IE를 같이 서비스해야 한다면 **요청 헤더를 통해서 확인**해서 요청 브라우저가 IE 계열인지 확인해서 다르게 처리하는 방식으로 처리해야합니다.  

<br>

### 응답 헤더 설정  

```
response.reset();

response.setContentType("application/octet-stream");
response.setHeader("Content-Description", "File Download");
```

**Content-Type 헤더를 `application/octet-stream`으로 설정**함으로써,  

응답을 브라우저에 직접 표시하는 대신 **다운로드해야 하는 바이너리 파일로 처리**하도록 웹 브라우저에 지시합니다.  

<br>

**Content-Description 헤더를 `File Download`로 설정** 함으로써,  

**다운로드할 파일이 포함되어 있음을 클라이언트나 브라우저에 표시하는 역할**을 합니다.  

즉, 응답 의도를 강화하는 목적으로 클라이언트에게 콘텐츠를 **다운로드 가능한 파일로 취급해야 한다는 명확한 표시**를 제공합니다.  

<br>

### 브라우저에 따른 파일 이름 인코딩

```
if (client.indexOf("MSIE") != -1) {
    response.setHeader("Content-Disposition", "attachment; filename=" + new String(originalFileName.getBytes("KSC5601"), "ISO8859_1"));
} else {
    originalFileName = new String(originalFileName.getBytes("utf-8"), "iso-8859-1");
    response.setHeader("Content-Disposition", "attachment; filename=\"" + originalFileName + "\"");
    response.setHeader("Content-Type", "application/octet-stream; charset=utf-8");
}
```  

변수 client에 **"MSIE"가 포함되어 있는지 확인**하여 사용자가 **Internet Explorer를 사용하고 있는지 확인**합니다.  

<br>

**인터넷 익스플로러를 사용한 사용자인 경우,** `KSC5601` 문자 인코딩과 `ISO8859_1` 인코딩을 사용하여 **파일 이름을 인코딩합니다.**  

변환 후에는 **Content-Disposition 헤더에 파일이름을 설정**합니다.  

<br>

**인터넷 익스플로러가 아닌 다른 브라우저인 경우,** 파일 이름이 `UTF-8` 및 `ISO-8859-1` **인코딩을 사용하여 파일 이름을 인코딩합니다.**  

변환 후에는 **Content-Disposition 헤더에 파일이름을 설정**합니다.  

또한, Content-Type 헤더는 `application/octet-stream; charset=utf-8`로 설정합니다.  

이는 응답 내의 텍스트 콘텐츠, 즉 파일 이름을 포함하여 **모든 텍스트 데이터가 올바르게 `UTF-8`로 해석되도록** 합니다.  

<br>

### 콘텐츠 길이 설정  

```
response.setHeader("Content-Length", String.valueOf(file.length()));
```

`Content-Length` 헤더는 **파일 길이(바이트)로 설정**됩니다. 이는 클라이언트에게 파일의 크기를 알려줍니다.  

<br>

### 바이너리 데이터 읽기 및 쓰기  

```
os = response.getOutputStream();

byte[] buffer = new byte[4096];
int bytesRead;

while ((bytesRead = in.read(buffer)) != -1) {
    os.write(buffer, 0, bytesRead);
}
```  

`getOutputStream()` 메소드는 **HttpServletResponse 클래스에서 제공하는 메서드**입니다. 

**응답 데이터를 쓸 수 있는 출력 스트림을 나타내는 OutputStream 개체를 반환**합니다.  

<br>

다음으로, 위 코드에서 **4096바이트 크기의 바이트 배열 `buffer`를 선언**했습니다.  

`while` 루프를 통해서, **`in` 입력 스트림은 데이터를 4096바이트씩 버퍼로 읽어옵니다.**  

입력 스트림의 `read()` 메서드는 스트림에서 최대 4096바이트의 데이터를 읽고 실제로 읽어들인 바이트 수를 반환하며, 이는 `byteRead` 변수에 저장됩니다.  

`read()` 메서드가 스트림의 끝에 도달하면 -1을 반환하여 파일의 끝을 의미합니다.  

<br>

while 루프 내에서는 `os.write(buffer, 0, bytesRead)` 버퍼의 내용을 출력 스트림 `os`에 씁니다.  

`write()` 메서드는 버퍼의 인덱스 0부터 시작해서 `byteRead` 바이트를 출력 스트림에 기록합니다.  

이를 통해 파일 데이터가 클라이언트로 스트리밍되어 다운로드 됩니다.  

여기서 의문이 들 수 있습니다.  

<br>

### 버퍼를 굳이 사용해야하나?  

자료를 `read()` 메서드로 한 바이트씩 읽는 것보다 **배열을 사용하여 한번에 읽으면 처리 속도가 훨씬 빠릅니다.**  


다음과 같은 테스트를 진행해보겠습니다.  

<p align="center">
  <img src="https://github.com/hbkuk/blog/assets/109803585/5ef91c74-0712-44ae-bee4-9b2e4f14b8e1" alt="text" width="number" />
</p>

#### read() 메서드로 한 바이트씩 끝까지 읽기  

<p align="center">
  <img src="https://github.com/hbkuk/blog/assets/109803585/7ae1b2ab-a943-46ab-8851-c16afe90d589" alt="text" width="number" />
</p>

`read()` 메서드로 파일을 읽는 경우 **파일의 끝에 도달하면 -1을 반환합니다.**  

while문을 보면 `read()` 메서드를 사용하여 **한 바이트씩 읽어 들이고 있습니다.**  

읽어 들여 저장한 i 값이 -1이 아닌 한 **while문이 계속 수행됩니다.**  

#### read(byte[] b) 메서드로 읽기  

<p align="center">
  <img src="https://github.com/hbkuk/blog/assets/109803585/7bc0be3b-9ef4-42c1-9dc9-6f6fe7d602c6" alt="text" width="number" />
</p>

`read(byte[] b)` 메서드는 선언한 **바이트 배열의 크기만큼 한꺼번에 자료를 읽습니다.**  

그리고 읽어 들인 자료의 수를 반환합니다.  

<br>

두 방식의 **속도차이는 어떨까요?**  

<p align="center">
  <img src="https://github.com/hbkuk/blog/assets/109803585/c69dd842-58ec-4171-bb92-9a27d6ee9e61" alt="text" width="number" />
</p>  

결과는 바이트 배열로 읽는 것이 약 **918.3배 빠릅니다.**  

따라서, 파일 다운로드를 구현할때, **버퍼를 사용하는 것이 권장될 수 있겠습니다.**  

<br>

### 버퍼의 크기는 어떻게 결정될까?  


비교적 큰 버퍼는 
- 장점: 데이터를 처리하는 데 필요한 **I/O 작업 수를 줄여 성능을 향상**
- 단점: 여러 동시 요청이나 제한된 리소스를 처리할 때 필요한 것보다 **더 많은 메모리를 사용**  

비교적 작은 버퍼는
- 장점: 불필요한 메모리를 사용하지 않음으로써, **메모리를 절약**
- 단점: **빈번한 I/O 작업으로 인해 성능 저하 초래**

일반적인 방법은 1024(1KB), 4096(4KB) 또는 8192(8KB)와 같이 **2의 배수인 버퍼 크기를 사용**하는 것입니다.  

</div>