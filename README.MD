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

# Roadmap

## basics
+ serialize JSON
+ deserialize JSON
+ save to db
+ syntax highlighting v1
++ https://gist.github.com/alehandrof/5361546
++ https://github.com/sublimehq/Packages/blob/master/C%2B%2B/C.sublime-syntax
+ unfold headline
+ queries v1
++ get all ticket headlines
++ find by topic

## timelogging
-- enter current ts
-- log in/out

## queries v2
-- find by name
-- find by date

## queries v3
-- syntax for complex queries

## gtd-cockpit
- prio A B C
- do-until
- render agenda
- improve inline syntax
- save and edit in inline mode
- ticket states TODO BLCK DLGT DONE

# visuals
- more colors for syntax highlighting

# ticket management
- delete tickets
- dirty state for tickets
- dirty state for reports
- fold headline

## ideas
- ticket links?
- in-text dialogs [YES] [NO]

## media files
-- link files 
-- link images
-- show images inline
