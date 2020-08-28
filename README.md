Instagram User Profiling
=============
> 관련참고 

>1. Twitter user 분석을 통한 유저 프로파일링

> https://drive.google.com/file/d/1qgz2XRHFCPFwVua7yPvOF1BC6RIpvKTj/view?usp=sharing

>2. 분석 요약

> https://drive.google.com/file/d/1qubUJwegZXw3iPdCarlQxtiA0oM8kg0a/view?usp=sharing

>3. 최종분석결과

> 현재 진행 중

### 프로젝트 내려받기
```python
git clone https://github.com/Dev-hottae/insta_profiling.git
```


### 인스타 태그를 통해 사용자 innerid 가져오기
```python
scrapy crawl insta_crawler -o <filename.json> -a hashtag="<tag>"
```

### 인스타 innerid 를 통해 사용자 히스토리 가져오기

> 중간에 429 에러로 인한 601초 중단 추가하였음, 초기 scrapy 활성화 시 직접 입력 가능

```python
scrapy crawl user_prof_crawler -o <filename.json> -a path="<filepath>"
```
