# ormcg
ormcg 是一个orm模板代码生成器， 目前只支持MySQL数据库Mybatis 框架模板代码生成，后续会加入对JPA、Mybatis_plus框架的支持。

### 1.为什么要写ormcg这个项目？

Mybatis 框架模板代码生成有两种方式，一是通过IDEA插件生成，如easyCode IDEA、MybatisX、MybatisX-Generator， easyCode IDEA是收费插件，

MybatisX-Generator 与MybatisX 虽然免费，但却依赖IDEA专业版数据库连接功能。二是Mybatis 官方提供的mybatis-generator，可以生成Mapper、xml文件，

缺点是mybatis-generator配置复杂，生成的Mapper没有做到Mybatis-plus 、 JPA 那样面向接口设计。

Mybatis-plus 接口设计

Mybatis-plus 的BaseMapper接口提供了一系列增删改查方法，使用时只需继承该接口，无需编写 mapper.xml 文件，即可获得CRUD功能。

``` java
@Repository
public interface StockBasicMapper extends BaseMapper<User> {
    //所有的CRUD已经编写完成
    //不需要像以前的配置一些xml

} ```
```

类似的，JPA的CrudRepository接口也提供了一系列增删改查方法，使用时只需继承该接口，即可获得CRUD功能。

``` //继承JpaRepository来完成对数据库的操作
@Repository
public interface StockBasiRepository extends JpaRepository<User,Integer> {
}
```

为了做到像Mybatis-plus、JPA那样便捷，参照Mybatis-plus、JPA接口设计，设计自动 生成Mapper接口层次，自动生成Mybatis Mapper、xml代码。

ormcg CrudRepository 接口层次图   

![](D:\dev\workspace\python\ormcg\docs\images\repository_hierarchy.png)

1. Repository:  该接口中没有方法，是一个标签接口;
2. ReadOnlyRepository: 只读接口，提供findAll与findOne通用查询方法;
3. CrudRepository : 提供用于增删改查方法的接口，;

 CrudRepository 接口方法介绍：

 - findAll: 动态查询方法，接受一个实体类对象作为参数，将查询条件对应的值设置到实体类对象对应字段上传入, 查询所有满足条件的数据。
	- findOne: 与findAll类似，也是动态查询方法，只不过只返回一条数据。

	- updateByIdDynamically：通过ID动态地更新数据，实体类对象对应字段的值不满足 Mybatis if 中的条件，则对应字段不更新。

	- updateByIdUsually： 通过ID更新数据， 相较于updateByIdDynamically，该方法没有 if 条件，直接将字段更新为实体类对象中设置的值。

- saveDynamically: 动态插入一条数据，实体类对象对应字段的值不满足 Mybatis if 中的条件，则插入时对应字段不设置值。

- saveUsually:  普通地插入一条数据，该方法没有 if 条件，直接将字段设置为实体类对象中设置的值。
- saveAll: 批量插入多条数据。

生成的Mapper继承自CrudRepository 接口，除了拥有以上方法外，还会生成以下常用方法：

- findByIdAndStatus: 通过主键ID、状态字段(用于数据的逻辑删除字段)查询数据；
- findByUniqueColumnInAndStatus： 通过主键集合或唯一索引字段集合、状态字段(用于数据的逻辑删除字段)查询数据；

与Mapper一样，生成的DAO同样继承自CrudRepository 接口， 是对Mapper中方法的再次封装。DAO中查询方法一般以query做前缀，Mapper中除了继承自CrudRepository 接口外的方法，一般都以find作为前缀。DAO中还提供使用Springboot @Async 注解的异步查询方法，异步方法以Async作为后缀，普通的同步方法以Sync做后缀。

### 2. ormcg 如何使用？

#### 2.1 ormcg 配置

开发环境配置示例, 以开发环境为例：

```
# 当前环境, 命令行参数未指定环境时, 使用该配置
profiles:
  active: dev
db:
  # 开发环境配置信息
  dev: 
   # SQLAlchemy 相关配置
    isolation_level: 'REPEATABLE READ'
    max_overflow: 3
    pool_size: 5
    pool_timeout: 120
    pool_recycle: 7200
    exclude_schema_name: [ mysql, information_schema, performance_schema, sys ]
    mysql_server:
      # mysql 配置信息
      db_name: information_schema
      host: your host
      port: your port
      username: username
      password: your password
      # 插入语句需要排除的列
      insert_exclude_columns: ['id', 'last_modified_by', 'last_modified_date']
      # 更新语句需要排除的列
      update_exclude_columns: ['id', 'created_by', 'created_date']
       # 查询语句 动态查询条件需要排除的列
      select_where_exclude_columns: ['created_by', 'created_date', 'last_modified_by', 'last_modified_date']

```

配置文件

#### 2.2 ormcg 命令行参数介绍

```
# 使用 --help 命令查看 命令行参数信息
orm --help
usage: ormcg [-h] [-A AUTHOR] [-E {dev,test,prod}] [-D {mysql,oracle,clickhouse}] [-H HOST] [-p PORT] [-S SCHEMA]
             table table_description

help to autogenerate orm code like mybatis mapper

positional arguments:
  table                 the table that you want to autogenerate orm code
  table_description     the description of table

options:
  -h, --help            show this help message and exit
  -A AUTHOR, --author AUTHOR
                        who generate this code
  -E {dev,test,prod}, --env {dev,test,prod}
                        database environment, available options [dev, test, product]
  -D {mysql,oracle,clickhouse}, --db {mysql,oracle,clickhouse}
                        what kind of database you are using
  -H HOST, --host HOST  the host of target database
  -p PORT, --port PORT  the port of target database
  -S SCHEMA, --schema SCHEMA
                        the schema that table you want to autogenerate orm code belong to
```

命令行参数

| 参数              | 含义                         | 是否必填 | 默认值       | 示例值            |
| ----------------- | ---------------------------- | -------- | ------------ | ----------------- |
| table             | 数据库表名                   | ✅        |              |                   |
| table_description | 数据库表描述                 | ✅        |              |                   |
| -A --author       | mapper作者                   | ❌        | autogenerate | --author==Bob     |
| -E --env          | 数据库环境                   | ❌        | dev          | --env=test        |
| -S --schema       | 数据库名                     | ❌        | analysis     | --schema=analysis |
| -D --db           | 数据库类型，暂时不可用       |          |              |                   |
| -H --host         | 数据库服务器host，暂时不可用 |          |              |                   |
| -p --port         | 数据库服务器端口，暂时不可用 |          |              |                   |



### 3. ormcg 背后原理

#### 2.1 **MySQL 元数据**

​	MySQL information_schema数据库是用于存储数据库表、表字段、表索引等元数据的数据库。

- **SCHEMATA表**：存放有关数据库的信息，可以在该表中使用 `SELECT * FROM  information_schema.`SCHEMATA 语句, 查看当前MySQL server 上数据库信息。

 - **COLUMNS表** :  存放有关表字段相关信息。

- **STATISTICS**：  存放有关表索引信息。

#### 2.2 ormcg 使用哪些依赖

- Python argparse： Python 命令行解析模块；

- Jinja2：模板引擎；
- SQLAlchemy：Python 语言下的 orm框架；
- Pyinstaller：将Python程序打包生成exe文件， pyinstaller -F main.py -n orm --add-data="templates;templates"；



​	

