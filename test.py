#! /usr/bin/env python3
try:
    import requests, json, time, os, random, re, datetime, sys, threading
    from rich.columns import Columns
    from rich import print as printf
    from rich.panel import Panel
    from rich.console import Console
    from requests.exceptions import RequestException
except (ModuleNotFoundError, ImportError) as error:
    print(f"[Error]: {error}!")
    exit()

SUKSES, GAGAL, CACHE = [], [], []

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def BANNER() -> None:
    clear()
    printf(
        Panel(
            r"""[bold red]●[bold yellow] ●[bold green] ●[/]
[bold blue] ______     **     **____     ______    
[bold blue]/\  == \   /\ \   /\  __ \   /\  == \   
[bold blue]\ \  **<   \ \ \  \ \  ** \  \ \  __<   
[bold blue] \ \_____\  \ \_\  \ \_\ \_\  \ \_\ \_\ 
[bold blue]  \/_____/   \/_/   \/_/\/_/   \/_/ /_/
        [underline white]Facebook Auto React - By BIAR""", 
            style="bold bright_black", 
            width=60
        )
    )

def DELAY(minutes: int, seconds: int, process_info: str) -> None:
    total = (minutes * 60 + seconds)
    while total:
        minutes, seconds = divmod(total, 60)
        printf(f"[bold bright_black]   ──>[bold green] {process_info}[bold white]/[bold green]{minutes:02d}:{seconds:02d}[bold white] SUCCESS:[bold green]{len(SUKSES)}[bold white] FAILED:[bold red]{len(GAGAL)}     ", end='\r')
        time.sleep(1)
        total -= 1
    printf(" " * 100, end='\r')  # Clear the line

class TokenManager:
    def __init__(self):
        self.token_path = "/storage/emulated/0/a/token.txt"
        self.tokens = self.load_tokens()
        os.makedirs(os.path.dirname(self.token_path), exist_ok=True)

    def load_tokens(self):
        try:
            if not os.path.exists(self.token_path):
                open(self.token_path, 'a').close()
                return []
            
            with open(self.token_path, 'r') as file:
                return [line.strip() for line in file if line.strip()]
        except:
            return []

    def save_token(self, token):
        if token not in self.tokens:
            with open(self.token_path, 'a') as file:
                file.write(f"{token}\n")
            self.tokens.append(token)
            return True
        return False

    def remove_token(self, token):
        if token in self.tokens:
            self.tokens.remove(token)
            with open(self.token_path, 'w') as file:
                file.write('\n'.join(self.tokens) + '\n' if self.tokens else '')
            return True
        return False

    def get_tokens(self):
        return self.tokens

class FacebookAutoReact:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9',
            'content-type': 'application/x-www-form-urlencoded'
        })
        self.token_manager = TokenManager()

    def extract_post_details(self, url):
        try:
            patterns = [
                r'\/(\d+)\/posts\/(\d+)',
                r'fbid=(\d+)',
                r'\/story\.php\?story_fbid=(\d+)\&id=(\d+)',
                r'\/(\d+)\/posts\/pfbid\w+',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    groups = match.groups()
                    if len(groups) == 2:
                        return {
                            'user_id': groups[0],
                            'post_id': groups[1],
                            'full_id': f"{groups[0]}_{groups[1]}"
                        }
                    elif len(groups) == 1:
                        return {
                            'post_id': groups[0],
                            'full_id': groups[0]
                        }
            return None
        except:
            return None

    def check_token(self, token):
        try:
            response = self.session.get(
                'https://graph.facebook.com/me',
                params={'access_token': token, 'fields': 'id,name'},
                timeout=15
            )
            if response.ok:
                data = response.json()
                return {
                    'valid': True,
                    'name': data.get('name'),
                    'id': data.get('id')
                }
            return {'valid': False}
        except:
            return {'valid': False}

    def perform_reaction(self, token, post_details, reaction_type):
        methods = [self._react_method_1, self._react_method_2, self._react_method_3]
        random.shuffle(methods)
        
        for method in methods:
            try:
                if method(token, post_details, reaction_type):
                    return True
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                printf(Panel(f"[bold red]Reaction method failed: {str(e)}", 
                    style="bold bright_black", width=60))
                continue
        return False

    def _react_method_1(self, token, post_details, reaction_type):
        url = f"https://graph.facebook.com/{post_details['full_id']}/reactions"
        params = {
            'type': reaction_type,
            'access_token': token
        }
        response = self.session.post(url, params=params, timeout=15)
        return response.ok

    def _react_method_2(self, token, post_details, reaction_type):
        url = f"https://graph.facebook.com/{post_details['post_id']}/reactions"
        data = {
            'type': reaction_type,
            'access_token': token,
            'method': 'post'
        }
        response = self.session.post(url, data=data, timeout=15)
        return response.ok

    def _react_method_3(self, token, post_details, reaction_type):
        url = "https://graph.facebook.com/graphql"
        reaction_map = {
            'LIKE': 1, 'LOVE': 2, 'HAHA': 4,
            'WOW': 3, 'SAD': 7, 'ANGRY': 8
        }
        
        feedback_id = f"feedback:{post_details['full_id']}"
        data = {
            'variables': json.dumps({
                'input': {
                    'feedback_id': feedback_id,
                    'feedback_reaction': reaction_map.get(reaction_type, 1),
                    'feedback_source': 'OBJECT',
                    'is_tracking_encrypted': True,
                    'tracking': [],
                    'actor_id': post_details.get('user_id', ''),
                    'client_mutation_id': str(random.randint(1, 1000000))
                }
            }),
            'access_token': token
        }
        response = self.session.post(url, data=data, timeout=15)
        return response.ok

def main():
    fb = FacebookAutoReact()
    
    while True:
        BANNER()
        
        printf(
            Panel(
                f"""[bold white][[bold green]1[bold white]] Add New Token
[bold white][[bold green]2[bold white]] View Tokens
[bold white][[bold green]3[bold white]] Start Auto React
[bold white][[bold green]4[bold white]] Exit Program""",
                style="bold bright_black",
                width=60,
                title="[bold bright_black]>> [Menu] <<",
                title_align="center",
                subtitle="[bold bright_black]╭───────",
                subtitle_align="left"
            )
        )
        
        choice = Console().input("[bold bright_black]   ╰─> ")
        
        if choice == '1':
            printf(
                Panel(f"[bold white]Enter your Facebook access token:", 
                    style="bold bright_black", 
                    width=60, 
                    title="[bold bright_black]>> [Add Token] <<", 
                    title_align="center",
                    subtitle="[bold bright_black]╭───────",
                    subtitle_align="left"
                )
            )
            token = Console().input("[bold bright_black]   ╰─> ")
            check_result = fb.check_token(token)
            if check_result['valid']:
                if fb.token_manager.save_token(token):
                    printf(Panel(f"[bold green]Token added successfully - User: {check_result['name']}", 
                        style="bold bright_black", width=60))
                else:
                    printf(Panel(f"[bold red]Token already exists", 
                        style="bold bright_black", width=60))
            else:
                printf(Panel(f"[bold red]Invalid token", 
                    style="bold bright_black", width=60))
            time.sleep(2)

        elif choice == '2':
            tokens = fb.token_manager.get_tokens()
            if tokens:
                valid_tokens = []
                printf(Panel("[bold white]Checking token validity...", 
                    style="bold bright_black", width=60))
                for i, token in enumerate(tokens, 1):
                    check_result = fb.check_token(token)
                    if check_result['valid']:
                        valid_tokens.append(token)
                        printf(Panel(f"[bold green]Token {i}: Valid - {check_result['name']}", 
                            style="bold bright_black", width=60))
                    else:
                        printf(Panel(f"[bold red]Token {i}: Invalid - Removed", 
                            style="bold bright_black", width=60))
                        fb.token_manager.remove_token(token)
                    
                printf(Panel(f"[bold white]Total valid tokens: [bold green]{len(valid_tokens)}", 
                    style="bold bright_black", width=60))
            else:
                printf(Panel(f"[bold red]No tokens saved", 
                    style="bold bright_black", width=60))
            input("\nPress Enter to continue...")

        elif choice == '3':
            tokens = fb.token_manager.get_tokens()
            if not tokens:
                printf(Panel(f"[bold red]No tokens available. Please add tokens first.", 
                    style="bold bright_black", width=60))
                time.sleep(2)
                continue

            printf(
                Panel(f"[bold white]Enter the post URL to react to:", 
                    style="bold bright_black", 
                    width=60, 
                    title="[bold bright_black]>> [Post URL] <<", 
                    title_align="center",
                    subtitle="[bold bright_black]╭───────",
                    subtitle_align="left"
                )
            )
            url = Console().input("[bold bright_black]   ╰─> ")
            post_details = fb.extract_post_details(url)
            
            if not post_details:
                printf(Panel(f"[bold red]Invalid post URL", 
                    style="bold bright_black", width=60))
                time.sleep(2)
                continue

            printf(
                Panel(
                    f"""[bold white]Available Reactions:
[bold white][[bold green]1[bold white]] LIKE
[bold white][[bold green]2[bold white]] LOVE
[bold white][[bold green]3[bold white]] HAHA
[bold white][[bold green]4[bold white]] WOW
[bold white][[bold green]5[bold white]] SAD
[bold white][[bold green]6[bold white]] ANGRY""",
                    style="bold bright_black",
                    width=60,
                    title="[bold bright_black]>> [Choose Reaction] <<",
                    title_align="center",
                    subtitle="[bold bright_black]╭───────",
                    subtitle_align="left"
                )
            )
            
            reaction_map = {
                '1': 'LIKE', '2': 'LOVE', '3': 'HAHA',
                '4': 'WOW', '5': 'SAD', '6': 'ANGRY'
            }
            
            reaction_choice = Console().input("[bold bright_black]   ╰─> ")
            if reaction_choice not in reaction_map:
                printf(Panel(f"[bold red]Invalid reaction choice", 
                    style="bold bright_black", width=60))
                time.sleep(2)
                continue

            printf(
                Panel(f"[bold white]Enter delay between reactions (seconds):", 
                    style="bold bright_black", 
                    width=60, 
                    title="[bold bright_black]>> [Delay] <<", 
                    title_align="center",
                    subtitle="[bold bright_black]╭───────",
                    subtitle_align="left"
                )
            )
            try:
                delay = float(Console().input("[bold bright_black]   ╰─> "))
            except:
                printf(Panel(f"[bold red]Invalid delay value", 
                    style="bold bright_black", width=60))
                time.sleep(2)
                continue

            printf(Panel("[bold green]Starting Auto React...", 
                style="bold bright_black", width=60))
            
            success_count = [0]
            failed_count = [0]
            lock = threading.Lock()

            def worker(token, index):
                try:
                    time.sleep(delay * index)
                    result = fb.perform_reaction(token, post_details, reaction_map[reaction_choice])
                    with lock:
                        if result:
                            success_count[0] += 1
                            printf(Panel(f"[bold green]Token {index + 1}: Reaction successful", 
                                style="bold bright_black", width=60))
                        else:
                            failed_count[0] += 1
                            printf(Panel(f"[bold red]Token {index + 1}: Reaction failed", 
                                style="bold bright_black", width=60))
                            fb.token_manager.remove_token(token)
                except Exception as e:
                    with lock:
                        failed_count[0] += 1
                        printf(Panel(f"[bold red]Token {index + 1}: Error - {str(e)}", 
                            style="bold bright_black", width=60))
                        fb.token_manager.remove_token(token)

            threads = []
            for i, token in enumerate(tokens):
                thread = threading.Thread(target=worker, args=(token, i))
                threads.append(thread)
                # Start all threads
            for thread in threads:
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            printf(
                Panel(
                    f"""[bold white]Auto React Summary:
[bold green]✓ Successful: {success_count[0]}
[bold red]✗ Failed: {failed_count[0]}
[bold white]≡ Remaining tokens: {len(fb.token_manager.get_tokens())}""",
                    style="bold bright_black",
                    width=60,
                    title="[bold bright_black]>> [Complete] <<",
                    title_align="center"
                )
            )
            input("\nPress Enter to continue...")

        elif choice == '4':
            printf(
                Panel(f"[bold green]Thanks for using Facebook Auto React Tool!", 
                    style="bold bright_black", 
                    width=60, 
                    title="[bold bright_black]>> [Goodbye] <<", 
                    title_align="center"
                )
            )
            break

        else:
            printf(
                Panel(f"[bold red]Invalid choice! Please try again.", 
                    style="bold bright_black", 
                    width=60, 
                    title="[bold bright_black]>> [Error] <<", 
                    title_align="center"
                )
            )
            time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        printf(
            Panel(f"[bold yellow]Program terminated by user", 
                style="bold bright_black", 
                width=60, 
                title="[bold bright_black]>> [Exit] <<", 
                title_align="center"
            )
        )
        sys.exit()
    except Exception as e:
        printf(
            Panel(f"[bold red]Fatal error: {str(e)}", 
                style="bold bright_black", 
                width=60, 
                title="[bold bright_black]>> [Error] <<", 
                title_align="center"
            )
        )
        sys.exit(1)
