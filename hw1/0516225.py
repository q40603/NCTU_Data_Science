from bs4 import BeautifulSoup
import os
import requests
import sys
import time
import re
from collections import Counter
from multiprocessing import Process,Pool
#-*-coding:utf-8-*-

class Tool(object):
	"""docstring for Tool"""
	def __init__(self):
		super(Tool, self).__init__()

		payload={
		'from':'/bbs/Beauty/index.html',
		'yes':'yes' 
		}
		self.rs = requests.session()
		res = self.rs.post('https://www.ptt.cc/ask/over18', data = payload)
		self.base_url = "https://www.ptt.cc"
		self.answer_push = {"like" : 0, "boo" : 0, "user_like": [], "user_boo" : []}
		self.answer_popular = {"bomb" : 0, "image" : []}
		self.answer_keyword = []
	
	def get_index_page(self, __id):
		r = self.rs.get("https://www.ptt.cc/bbs/Beauty/index{}.html".format(str(__id)))
		if (r.status_code == 500):
			return {
				"success" : 0,
				"html" : ""
			}
		else:
			#print(r.text)
			return {
				"success" : 1,
				"html" : r.text
			}

	def get_sub_page(self, url):
		#self.headers["refer"] = "https://www.ptt.cc/bbs/Beauty/index{}.html".format(str(__id))
		r = self.rs.get(url)
		#print(r)
		if (r.status_code == 500):
			return {
				"success" : 0,
				"html" : ""
			}
		else:
			#print(r.text)
			return {
				"success" : 1,
				"html" : r.text
			}

	def parse_crawl(self, content, __id, begin, stop):
		soup = BeautifulSoup(content, 'html.parser')
		r1= soup.find_all("div", class_="r-ent")
		for i in r1:
			r2 = i.find(class_="title")
			r3 = i.find(class_="date")
			r4 = i.find(class_="hl f1")
			try:
				__date = r3.text.replace("/","").lstrip(" ")
				__title = r2.a.text
				__href = self.base_url + r2.a.get("href")

				if re.search(r"\[公告\]", __title):
					continue

				if (__id == begin and __date == "1231"):
					continue

				if (__id == stop-1 and __date == "101"):
					break
					
			except Exception : 
				continue

			else:
				with open("all_articles.txt", "a", encoding="utf-8") as text_file:
					print("{},{},{}".format(__date,__title,__href),file=text_file)

				if r4 and r4.text == "爆":
					with open("all_popular.txt", "a", encoding="utf-8") as text_file:
						print("{},{},{}".format(__date,__title,__href),file=text_file)	


	def append_push_Result(self, result):
		#print(result)
		self.answer_push["like"] += result["like"]
		self.answer_push["boo"] += result["boo"]
		self.answer_push["user_like"].extend(result["user_like"])
		self.answer_push["user_boo"].extend(result["user_boo"])
		#print(self.answer_push)

	def parse_push_sub(self,content):
		#print(content)
		soup = BeautifulSoup(content, 'html.parser')
		r1= soup.find_all("div", class_="push")
		response = {
			"like" : 0,
			"boo" : 0,
			"user_like" : [],
			"user_boo" : []
		}
		for i in r1:
			r2 = i.find(class_="push-tag")
			r4 = i.find(class_="f3 hl push-userid")

			
			try:
				push_tag = r2.text.rstrip()
				push_id = r4.text

			except Exception : 
				continue

			else:				
				if(push_tag == "推"):
					response["like"] += 1
					response["user_like"].append(push_id)

				elif(push_tag == "噓"):
					response["boo"] += 1
					response["user_boo"].append(push_id)					
		return response


	def summarize_push(self, start, end):
		print("summarizing_push........")
		self.answer_push["like_rank"] = sorted(dict(Counter(self.answer_push["user_like"])).items(), key=lambda x: (-x[1], x[0]))
		#
		self.answer_push["boo_rank"] = sorted(dict(Counter(self.answer_push["user_boo"])).items(), key=lambda x: (-x[1], x[0]))
		#OrderedDict(Counter(self.answer_push["user_boo"]))
		with open("push[{}-{}].txt".format(start,end), "a", encoding="utf-8") as text_file:
			print("all like: {}".format(self.answer_push["like"]),file=text_file)
			print("all boo: {}".format(self.answer_push["boo"]),file=text_file)
			for i in range(10):
				print("like #{}: {} {}".format(i+1, self.answer_push["like_rank"][i][0],self.answer_push["like_rank"][i][1]),file=text_file)
			for i in range(10):
				print("boo #{}: {} {}".format(i+1, self.answer_push["boo_rank"][i][0],self.answer_push["boo_rank"][i][1]),file=text_file)

	def append_popular_Result(self,result):
		#print(result)
		self.answer_popular["image"].extend(result)

	def parse_popular_sub(self,content):
		soup = BeautifulSoup(content, 'html.parser')
		r1= soup.find_all('a')
		response = []
		for i in r1:
			# print(i["href"])
			if i["href"].lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
				response.append(i["href"])
				#print(i["href"]," append")				
		return response

	def summarize_popular(self, start, end, _id):
		print("summarizing_popular........")
		with open("popular[{}-{}].txt".format(start,end), "a", encoding="utf-8") as text_file:
			print("number of popular articles: {}".format(_id), file=text_file)
			for i in self.answer_popular["image"]:
				print(i,file=text_file)


	def append_keyword_Result(self,result):
		#print(result)
		self.answer_keyword.extend(result)

	def parse_keyword_sub(self,keyword, content):
		response = []
		#print(content.text)
		soup = BeautifulSoup(content, 'html.parser')
		# check_content= soup.find_all('div', {'id': 'main-container'})
		check_content = soup.get_text().split("--\n※ 發信站")[0].split("返回看板")[1]
		if re.search(keyword, check_content):
			print("True")		
			r1= soup.find_all('a')			
			for i in r1:
				# print(i["href"])
				if i["href"].lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
					response.append(i["href"])
					#print(i["href"]," append")				
		return response

	def summarize_keyword(self, keyword, start, end):
		print("summarizing_keyword........")
		with open("keyword({})[{}-{}].txt".format(keyword,start,end), "a", encoding="utf-8") as text_file:
			for i in self.answer_keyword:
				print(i,file=text_file)		

class Crawl(object):
	"""docstring for Crawl"""
	def __init__(self,cmd):
		super(Crawl, self).__init__()
		self.tool = Tool()
		command_exec = getattr(self, cmd[1], None)
		self.begin = 2324
		self.stop = 2759
		if command_exec:
			command_exec(*cmd[2:])
		else:
			print("wrong format")

	def crawl(self):
		print("crawling....")

		for __id in range(self.begin,self.stop) :
			print("crawling......{}".format(__id))
			r = self.tool.get_index_page(__id)

			if not r["success"]:
				break

			self.tool.parse_crawl(r["html"], __id, self.begin,self.stop)
			#print(r2)
			__id += 1

			if not __id%20:
				time.sleep(1.5)
			# r2 = soup2.find_all("title")
			# print(r2.text)

	def push(self, start, end):
		print("pushing.... start={} end ={}".format(start,end))
		text_file = open("./all_articles.txt","r+")
		__id = 0
		pool = Pool(processes=2)

		for url in text_file.readlines():
			__date = url.split(",")[0]
			if (int(__date) > int(end)) or (int(__date) < int(start)):
				print("skip", __date)
				continue

			__href = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url)[0]
			print("crawling......{}".format(__href))

			content = self.tool.get_sub_page(__href)
			t = pool.apply_async(self.tool.parse_push_sub, (content["html"],), callback=self.tool.append_push_Result)
			
			__id += 1

			if not __id%20:
				time.sleep(1)
		pool.close()
		pool.join()	

		self.tool.summarize_push(start, end)


	def popular(self, start, end):
		print("popular.... start={} end ={}".format(start,end))

		text_file = open("./all_popular.txt","r+")
		__id = 0
		pool = Pool(processes=2)

		for url in text_file.readlines():

			__date = url.split(",")[0]

			if (int(__date) > int(end)) or (int(__date) < int(start)):
				print("skip", __date)
				continue

			__href = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url)[0]
			r = self.tool.get_sub_page(__href)
			print("crawling......{}".format(__href))

			if not r["success"]:
				break

			content = self.tool.get_sub_page(__href)
			t = pool.apply_async(self.tool.parse_popular_sub, (content["html"],), callback=self.tool.append_popular_Result)
			__id += 1

			if not __id%20:
				time.sleep(1)

		pool.close()
		pool.join()	
		self.tool.summarize_popular(start, end, __id)

	def keyword(self, keyword, start, end):
		print("keyword.... keyword={} start={} end={}".format(keyword, start,end))

		text_file = open("./all_articles.txt","r+")
		__id = 0
		pool = Pool(processes=2)

		for url in text_file.readlines():
			__date = url.split(",")[0]
			
			if (int(__date) > int(end)) or (int(__date) < int(start)):
				print("skip", __date)
				continue

			__href = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url)[0]
			r = self.tool.get_sub_page(__href)
			print("crawling......{}".format(__href))

			if not r["success"]:
				break

			content = self.tool.get_sub_page(__href)
			t = pool.apply_async(self.tool.parse_keyword_sub, (keyword,content["html"],), callback=self.tool.append_keyword_Result)
			__id += 1


			if not __id%20:
				time.sleep(1)

		pool.close()
		pool.join()	
		self.tool.summarize_keyword(keyword, start, end)



if __name__ == '__main__':
	Crawl(sys.argv)