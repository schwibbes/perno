# concept
- ctrl-enter calls plugin
- context at cursor decides what to do
-- selected text starts with 'NOTE' save ticket
-- selected text: execute as action

#short-format
NOTE: this is the first line... #(topic) ~id

# long format
NOTE: first line is title
#(topic) 
#(can have more than one!)
$(linked file.gif)
@(2017-10-28T08:23:01) - (2017-10-28T08:40:01)
text
more text

#todo
+ serialize JSON
+ deserialize JSON
+ save to db
- actions
++ get all ticket headlines
-- find by name
-- find by date
++ find by topic
- syntax highlighting
- fold/unfold headline
- delete