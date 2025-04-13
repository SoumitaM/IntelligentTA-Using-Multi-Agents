from crew import create_crew

def get_user_command():
    print("\n--- Welcome to Intelligent TA Assistant ---")
    print("Some example prompts you can use:")
    print("• Give me the names of 4 applicants who are best suited for the job profile of Java developer")
    print("• Schedule a meeting with Applicant A on 29th February, 2026 from 10 am")
    print("• Message applicant B asking if they’re available this weekend\n")

    return input("💬 Your Command: ")

if __name__ == "__main__":
    crew = create_crew()

    while True:
        command = get_user_command()

        if command.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        result = crew.kickoff(inputs={"job_description": command})
        print("\n🧠 Final Result:\n", result)
