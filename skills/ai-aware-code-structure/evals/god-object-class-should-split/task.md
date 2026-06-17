# Is a 420-line UserService god object the right call?

I have a UserService TypeScript class that's about 420 lines. It handles auth-token issuing and validation, profile CRUD against the database, sending transactional emails, and firing analytics events. It's all in one file. My reasoning was that keeping it together means Claude has everything in one place and never has to go hunting. Is that the right call?
