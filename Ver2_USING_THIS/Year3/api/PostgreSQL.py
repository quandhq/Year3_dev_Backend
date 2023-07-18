# import psycopg2

# class PostgreSQL:
#     database: str = None
#     user: str = None
#     password: str = None
#     host: str = None
#     port: str = None
#     cur: psycopg2.connect() = None
#     def __init__(self, __database = "farm", 
#                     __user = "quan",
#                     __password = "1",
#                     __host = "localhost",
#                     __port = "5432",):
#         self.database = __database
#         self.user = __user
#         self.password = __password
#         self.host = __host
#         self.port = __port
#         self.cur = psycopg2.connect()
#     # a function that try to connect to a database and return a cursor

#     # a function that trys to create a database in the table 

#     # a fucntion that trys to insert record to database 