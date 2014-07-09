# Be sure to restart your server when you modify this file.

# Your secret key is used for verifying the integrity of signed cookies.
# If you change this key, all old signed cookies will become invalid!

# Make sure the secret is at least 30 characters and all random,
# no regular words or you'll be exposed to dictionary attacks.
# You can use `rake secret` to generate a secure secret key.

# Make sure your secret_key_base is kept private
# if you're sharing your code publicly.
Server::Application.config.secret_key_base = '8a41cf898f3ac8401f6abba0dc808d516542610d1092a164cb6977e6d6b1da3449c6d93bf3f02baa7983efbcd31ce98543f03305aaa2c13b06ff77f4501db449'
