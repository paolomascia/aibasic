# AIBasic v1.0 - Quick Reference

## Syntax

```aibasic
<line_number> <instruction>
<line_number> (task_type) <instruction>
# Comment
```

## Control Flow

| Construct | Syntax | Example |
|-----------|--------|---------|
| **Unconditional Jump** | `goto <line>` | `30 goto 100` |
| **Conditional Jump** | `if <condition> jump to <line>` | `40 if x > 10 jump to line 100` |
| **Error Handler** | `on error goto <line>` | `50 on error goto 900` |
| **Call Subroutine** | `call <line>` | `60 call 1000` |
| **Return** | `return` | `1020 return` |

## Task Types (36)

### Data
- `csv`, `excel`, `json`, `xml`, `df`

### Databases (Modules)
- `postgres`, `mysql`, `mongodb`, `cassandra`, `redis`

### Messaging (Modules)
- `rabbitmq`, `kafka`

### Search (Module)
- `opensearch`

### Storage (Module)
- `s3`, `compress`

### Network (Modules)
- `api`, `ssh`, `email`, `web`

### Security (Module)
- `vault`, `crypto`

### Processing
- `math`, `plot`, `ml`, `image`

### Utility
- `fs`, `text`, `pdf`, `date`, `log`, `config`, `shell`, `rpa`, `stream`

## Modules (14)

| Module | Config Section | Common Operations |
|--------|---------------|-------------------|
| **PostgreSQL** | `[postgres]` | connect, query, insert, update, transaction |
| **MySQL** | `[mysql]` | connect, query, insert, update, transaction |
| **MongoDB** | `[mongodb]` | find, insert, update, delete, aggregate |
| **Cassandra** | `[cassandra]` | query, insert, batch, prepared statements |
| **Redis** | `[redis]` | get, set, incr, expire, lpush, rpop |
| **RabbitMQ** | `[rabbitmq]` | publish, consume, declare, bind |
| **Kafka** | `[kafka]` | produce, consume, commit, subscribe |
| **OpenSearch** | `[opensearch]` | index, search, aggregate, delete |
| **Email** | `[email]` | send, attach, HTML template |
| **S3** | `[s3]` | upload, download, list, presigned URL |
| **SSH** | `[ssh]` | execute, sftp upload/download, tunnel |
| **Vault** | `[vault]` | read, write, delete secret |
| **Compression** | `[compress]` | compress, extract, list |
| **REST API** | `[restapi]` | GET, POST, PUT, DELETE, auth |

## Special Variables

### Error Handling
- `_last_error` - Exception object
- `_last_error_line` - Line number of error
- `_error_handler` - Current error handler line

### Control Flow
- `_next_line` - Next line to execute
- `_current_line` - Currently executing line
- `_call_stack` - Subroutine return addresses

## Common Patterns

### Loop
```aibasic
10 set i to 0
20 print i
30 increment i by 1
40 if i < 10 jump to line 20
```

### Error Handling
```aibasic
10 on error goto 100
20 # risky operation
30 goto 200
100 print "Error:" and _last_error
200 print "Done"
```

### Subroutine
```aibasic
10 call 1000
20 goto 999
1000 # subroutine code
1020 return
999 print "End"
```

### File Processing
```aibasic
10 (csv) read file "data.csv"
20 (df) filter where age > 18
30 (excel) save to "output.xlsx"
```

### Database Query
```aibasic
10 (postgres) connect to database
20 (postgres) query "SELECT * FROM users"
30 (df) transform data
40 (csv) export to file
```

## Compilation

```bash
# Compile
python src/aibasic/aibasicc.py -c config.conf -i input.aib -o output.py

# Run
python output.py
```

## Configuration Template

```ini
[llm]
API_URL = https://api.openai.com/v1/chat/completions
API_TOKEN = your-key
MODEL = gpt-4o-mini

[postgres]
HOST = localhost
DATABASE = mydb
USERNAME = user
PASSWORD = pass

[mongodb]
CONNECTION_STRING = mongodb://localhost:27017

[redis]
HOST = localhost
PORT = 6379

[s3]
AWS_ACCESS_KEY_ID = key
AWS_SECRET_ACCESS_KEY = secret

[ssh]
HOST = server.com
USERNAME = admin
KEY_FILE = ~/.ssh/id_rsa
```

## Best Practices

✅ **DO:**
- Use line numbers 10, 20, 30... for easy insertion
- Use 1000+, 2000+ for subroutines
- Add comments to document logic
- Use task type hints for clarity
- Set error handlers before risky operations
- Always include RETURN in subroutines

❌ **DON'T:**
- Create infinite loops without exit condition
- Forget RETURN statement
- Jump into middle of subroutines
- Mix main code with subroutine code
- Ignore error handling for I/O operations

## Examples

### Data Pipeline
```aibasic
10 (csv) read "sales.csv" into data
20 (df) filter where revenue > 1000
30 (df) group by region, sum revenue
40 (postgres) save to database
```

### Server Automation
```aibasic
10 (ssh) connect to server
20 (ssh) execute "uptime"
30 (ssh) transfer file to remote
40 print "Deploy complete"
```

### Message Processing
```aibasic
10 (rabbitmq) consume from queue
20 on error goto 100
30 (api) POST to endpoint
40 goto 10
100 print "Error:" and _last_error
110 goto 10
```

## Resources

- Complete Guide: `docs/COMPLETE_GUIDE.md`
- Modules Guide: `MODULES_GUIDE.md`
- Task Types: `TASK_TYPES.md`
- Jumps Guide: `JUMPS_GUIDE.md`
- Examples: `examples/`

---

**AIBasic v1.0** | © 2025 | Natural Language Programming
