import Mustache from "./mustache";

const stepsData = {
    steps: [
        {
            number: 1,
            title: "Discord 개발자 포털 접속",
            content: "웹 브라우저를 열고 Discord 개발자 포털에 접속합니다.",
            imageAlt: "Discord 개발자 포털 메인 화면"
        },
        {
            number: 2,
            title: "디스코드 계정으로 로그인",
            content: "아직 로그인하지 않았다면, 디스코드 계정으로 로그인합니다.",
            imageAlt: "디스코드 로그인 화면"
        },
        {
            number: 3,
            title: "새로운 애플리케이션 생성",
            content: `
                <ul>
                    <li>우측 상단의 "New Application" 버튼을 클릭합니다.</li>
                    <li>팝업 창에서 애플리케이션의 이름을 입력하고 "Create" 버튼을 클릭합니다.</li>
                </ul>
            `,
            imageAlt: "새 애플리케이션 생성 화면"
        },
        {
            number: 4,
            title: "애플리케이션 정보 설정",
            content: `
                <ul>
                    <li>애플리케이션이 생성되면 "General Information" 페이지로 이동합니다.</li>
                    <li>필요에 따라 아이콘, 설명 등을 설정할 수 있습니다.</li>
                    <li>설정이 완료되면 하단의 "Save Changes" 버튼을 클릭하여 변경사항을 저장합니다.</li>
                </ul>
            `,
            imageAlt: "애플리케이션 정보 설정 화면"
        },
        {
            number: 5,
            title: "봇 추가",
            content: `
                <ul>
                    <li>좌측 메뉴에서 "Bot" 탭을 선택합니다.</li>
                    <li>"Add Bot" 버튼을 클릭합니다.</li>
                    <li>확인 메시지가 나타나면 "Yes, do it!"을 클릭하여 봇을 생성합니다.</li>
                </ul>
            `,
            imageAlt: "봇 추가 화면"
        },
        {
            number: 6,
            title: "봇 토큰 발급 및 복사",
            content: `
                <ul>
                    <li>봇이 생성되면 "Username" 아래에 봇의 정보가 나타납니다.</li>
                    <li>"Token" 섹션에서 "Click to Reveal Token" 또는 "Reset Token" 버튼을 클릭하여 토큰을 확인합니다.</li>
                    <li>나타난 토큰을 복사합니다.</li>
                </ul>
                <div class="warning">
                    <strong>주의:</strong> 이 토큰은 봇의 비밀번호와 같으므로 절대로 공개적으로 공유하면 안 됩니다.
                </div>
            `,
            imageAlt: "봇 토큰 발급 화면"
        },
        {
            number: 7,
            title: "봇 권한 설정 (선택 사항)",
            content: `
                <ul>
                    <li>"Privileged Gateway Intents" 섹션에서 필요한 인텐트를 활성화합니다.</li>
                    <li>예: "Presence Intent", "Server Members Intent", "Message Content Intent" 등</li>
                    <li>인텐트를 활성화한 후 하단의 "Save Changes" 버튼을 클릭하여 변경사항을 저장합니다.</li>
                </ul>
            `,
            imageAlt: "봇 권한 설정 화면"
        },
        {
            number: 8,
            title: "봇을 서버에 추가",
            content: `
                <ul>
                    <li>좌측 메뉴에서 "OAuth2" > "URL Generator"를 클릭합니다.</li>
                    <li>"Scopes" 섹션에서 "bot"을 선택합니다.</li>
                    <li>"Bot Permissions"에서 봇에게 부여할 권한을 선택합니다.</li>
                    <li>예: "Send Messages", "Manage Roles", "Kick Members" 등</li>
                    <li>하단에 생성된 URL을 복사합니다.</li>
                    <li>새로운 브라우저 탭을 열고 복사한 URL을 붙여넣어 접속합니다.</li>
                    <li>봇을 추가할 서버를 선택하고 "Authorize" 버튼을 클릭하여 봇을 서버에 초대합니다.</li>
                </ul>
            `,
            imageAlt: "봇 서버 추가 화면"
        },
        {
            number: 9,
            title: "봇 개발 시작",
            content: "이제 복사한 토큰을 사용하여 디스코드 봇을 개발할 수 있습니다.",
            imageAlt: "봇 개발 시작 화면"
        }
    ]
};

const template = document.getElementById('steps-container').innerHTML;
const rendered = Mustache.render(template, stepsData);
document.getElementById('steps-container').innerHTML = rendered;