import scrapy


class Test1Spider(scrapy.Spider):
    name = "test1"
    allowed_domains = ["careerbuilder.vn"]
    start_urls = ["https://careerbuilder.vn/viec-lam/ngay-cap-nhat-d1-vi.html"]

    def parse(self, response):
        for job in response.xpath("//div[@class='main-slide']/div[1]/div"):
            job_title = job.xpath(".//div/div[2]/div[1]/h2/a/@title").get()
            yield {
                    "job_title": job_title
                }
        next_page = response.xpath("//div[@class='main-slide']/div[2]/ul/li[@class ='next-page']/a/@href").get()


        if next_page:
            print("\n\n"+(next_page.center(180, "=")+"\n")*7+"\n")
            yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse, headers={
                                    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
                                })
        pass
