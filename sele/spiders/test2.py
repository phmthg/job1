import scrapy
import re



class Test2Spider(scrapy.Spider):
    # Problem: https://careerbuilder.vn/vi/tim-viec-lam/nhan-vien-ke-toan-thue.35BB1BAD.html can not be scraped (subset of 5% can not be scraped)
    #          https://careerbuilder.vn/vi/tim-viec-lam/tro-ly-kinh-doanh-tieng-trung.35BB74DD.html
    #          https://careerbuilder.vn/vi/tim-viec-lam/ke-toan-vien.35BB66AA.html

    # First, scrape entire, then, 3 days scrape once
    # 11/03 run 2 weeks ago, 16/03 run 3 days ago
    # scrapy crawl careerbuilder -o all_Test2s_cb_202303110948.csv
    name = 'test2'
    allowed_domains = ['careerbuilder.vn']

    def start_requests(self):
        yield scrapy.Request(url='https://careerbuilder.vn/viec-lam/tat-ca-viec-lam-vi.html',
                            callback=self.parse,
                            headers = {
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
                                'Referer': 'https://careerbuilder.vn/viec-lam/ngay-cap-nhat-d1-vi.html',
                                'Accept-Language': 'en-US,en;q=0.9',
                            })

    def parse(self, response):
        for job in response.xpath("//div[@class='main-slide']/div[position() = 1]/div"):
            job_title = job.xpath(".//div/div[position() = 2]/div[position() = 1]/h2/a/@title").get()
            job_url = job.xpath(".//div/div[position() = 2]/div[position() = 1]/h2/a/@href").get()

            company_title = job.xpath(".//div/div[position() = 2]/div[position() = 2]/a[position() = 1]/@title").get()

            salary = job.xpath(".//div/div[position() = 2]/div[position() = 2]/a[position() = 2]/div[position() = 1]/p/text()").get()

            location = " |".join(job.xpath(".//div/div[position() = 2]/div[position() = 2]/a[position() = 2]/div[position() = 2]/ul/li/text()").getall())

            posting_date = job.xpath(".//div/div[position() = 2]/div[position() = 3]/div/time/text()").get()

            yield response.follow(
                url=job_url,
                callback=self.parse_job,
                meta={
                    "job_title": job_title,
                    "job_url": response.urljoin(job_url),
                    "company_title": company_title,
                    "salary": salary,
                    "location": location,
                    "posting_date": posting_date,
                },
            )

        next_page = response.xpath("//div[@class='main-slide']/div[position() = 2]/ul/li[@class = 'next-page']/a/@href").get()

        if next_page:
            print("\n\n"+(next_page.center(180, "=")+"\n")*7+"\n")
            yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse, headers={
                                    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
                                })

    def parse_job(self, response):
        job_title = response.request.meta['job_title']
        job_url = response.request.meta['job_url']
        company_title = response.request.meta['company_title']
        salary = response.request.meta['salary']
        location = response.request.meta['location']
        posting_date = response.request.meta['posting_date']

        age = response.xpath("//section[@class='job-detail-content']/div[5]/div/ul/li[contains(text(), 'Độ tuổi')]/text()").get()
 

        sex= response.xpath("//section[@class='job-detail-content']/div[5]/div/ul/li[contains(text(), 'Giới tính')]/text()").get() 
        
        edu_level= response.xpath("//section[@class='job-detail-content']/div[5]/div/ul/li[contains(text(), 'Bằng cấp')]/text()").get()

        
        industry = " | ".join(list(map(lambda x: x.strip().strip("\r\n").strip(),
            response.xpath("//section[@class = 'job-detail-content']/div[@class = 'bg-blue']/div/div[position() = 2]/div/ul/li[position() = 2]/p/a/text()").getall())))
        if not industry:
            industry = " | ".join(response.xpath("//div[@class = 'bottom-template']/div/div/div[position() = 1]/div[@class = 'box-info']/div/div/table/tbody/tr[position() = 1]/td[position() = 2]/a/text()").getall())

        job_type = response.xpath("//section[@class = 'job-detail-content']/div[@class = 'bg-blue']/div/div[position() = 2]/div/ul/li[position() = 3]/p/text()").get()
        if not job_type:
            job_type = response.xpath("//div[@class = 'bottom-template']/div/div/div[position() = 1]/div[@class = 'box-info']/div/div/table/tbody/tr[position() = 3]/td[position() = 2]/p/text()").get()

        exp = response.xpath("//section[@class = 'job-detail-content']/div[@class = 'bg-blue']/div/div[position() = 3]/div/ul/li[position() = 2]/p/text()").get()
        if exp:
            exp = self.cleanse_exp(exp)
        else:
            exp = response.xpath("//div[@class = 'bottom-template']/div/div/div[position() = 1]/div[@class = 'box-info']/div/div/table/tbody/tr[position() = 6]/td[position() = 2]/p/text()").get()
            if exp:
                exp = self.cleanse_exp(exp)

        position = response.xpath("//section[@class = 'job-detail-content']/div[@class = 'bg-blue']/div/div[position() = 3]/div/ul/li[position() = 3]/p/text()").get()
        if not position:
            position = response.xpath("//div[@class = 'bottom-template']/div/div/div[position() = 1]/div[@class = 'box-info']/div/div/table/tbody/tr[position() = 5]/td[position() = 2]/p/text()").get()

        expiration_date = response.xpath("//section[@class = 'job-detail-content']/div[@class = 'bg-blue']/div/div[position() = 3]/div/ul/li[position() = 4]/p/text()").get()
        if not expiration_date:
            expiration_date = response.xpath("//div[@class = 'bottom-template']/div/div/div[position() = 1]/div[@class = 'box-info']/div/div/table/tbody/tr[position() = 7]/td[position() = 2]/p/text()").get()

        job_tags = " | ".join(response.xpath("//section[@class = 'job-detail-content']/div[position() = 7]/ul/li/a/text()").getall())
        if not job_tags:
            job_tags = " | ".join(list(map(lambda x: x.strip(), response.xpath("//div[@class = 'bottom-template']/div/div/div[position() = 1]/div[@class = 'full-content']/div[position() = 4]/ul/li/a/text()").getall())))

        yield {
            "job_title": job_title,
            "company_title": company_title,
            "salary": salary,
            "location": location,
            "posting_date": posting_date,
            "expiration_date": expiration_date,
            "industry": industry,
            "job_type": job_type,
            "exp": exp,
            "position": position,
            "age": age,
            "sex": sex,
            "edu_level": edu_level,
            "job_tags": job_tags
        }

    def cleanse_exp(self, raw_string):
        """
        raw_string = '\r\n     Trên    2 \r\n        Năm\r\n          '
        
        Phase 1: '\r\n     Trên    2 \r\n        Năm\r\n          '
            --> 'Trên    2 Năm'
        
        Phase 2: 'Trên    2 Năm'
            --> 'Trên 2 Năm'
        """
        
        raw_string = raw_string.strip()
        pat = '(\\r\\n[\s]*)'
        for m_start_end in reversed([(m.start(0), m.end(0)) for m in re.finditer(pat, raw_string)]):
            raw_string = raw_string[:m_start_end[0]] + "" + raw_string[m_start_end[1]:]
        
        pat = '[\s]{2,}'
        for m_start_end in reversed([(m.start(0), m.end(0)) for m in re.finditer(pat, raw_string)]):
            raw_string = raw_string[:m_start_end[0]] + " " + raw_string[m_start_end[1]:]
        
        return raw_string