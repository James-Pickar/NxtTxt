input_mode = "777"
output_mode: int = 0o777
int("0o777")

if input_mode:
    try:
        int(input_mode)
    except ValueError:
        print(input_mode, "is not a valid unix permission level.")
        exit(1)
else:
    output_mode = int("0o" + input_mode)
print(output_mode)
