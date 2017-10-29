# concept
- CMD + enter calls plugin
- context at cursor decides what to do
-- selected text starts with 'NOTE' -> save ticket
-- selected text: execute as action
--- ? -> find all tickets
--- @today -> find all with ts of today
--- #topic -> find all with topic 'topic'


#short-format
```
*NOTE: this is the first line... #(topic) ~id
```

# long format
```
NOTE: first line is title
#(topic) 
#(can have more than one!)
$(linked file.gif)
~59f5785815614201fe8e4322
@(2017-10-28T08:23:01) - (2017-10-28T08:40:01)
text
more text
```

#todo
+ serialize JSON
+ deserialize JSON
+ save to db
- actions
++ get all ticket headlines
-- find by name
-- find by date
++ find by topic
+ syntax highlighting v1
-- https://gist.github.com/alehandrof/5361546
-- https://github.com/sublimehq/Packages/blob/master/C%2B%2B/C.sublime-syntax
- syntax highlighting v2
- dirty state for tickets
- dirty state for reports
- fold headline
+ unfold headline
- delete tickets
- link files
- link images
