<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI洞察日报订阅</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 min-h-screen">
    <div class="container mx-auto px-4 py-8 max-w-2xl">
        <div class="bg-white rounded-lg shadow-md p-8">
            <!-- Header -->
            <div class="text-center mb-8">
                <h1 class="text-3xl font-bold text-gray-800 mb-2">📡 AI洞察日报订阅</h1>
                <p class="text-gray-600">每天早上09:00，林克会准时为您推送AI行业最新动态</p>
            </div>

            <!-- Login Section -->
            <div id="loginSection">
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
                    <h2 class="text-lg font-semibold text-blue-800 mb-3">🔐 快手SSO登录</h2>
                    <p class="text-blue-700 mb-4">请先登录快手账号，订阅功能仅限快手内部员工使用</p>
                    <button id="loginBtn" class="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 transition-colors">
                        登录快手SSO
                    </button>
                </div>
            </div>

            <!-- Subscription Section (Hidden by default) -->
            <div id="subscriptionSection" class="hidden">
                <div class="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
                    <div class="flex items-center justify-between mb-4">
                        <h2 class="text-lg font-semibold text-green-800">✅ 当前订阅状态</h2>
                        <span id="statusBadge" class="px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                            已订阅
                        </span>
                    </div>
                    <div class="text-green-700">
                        <p class="mb-2">👤 用户名：<span id="usernameDisplay" class="font-medium"></span></p>
                        <p>📅 订阅时间：<span id="subscribedAtDisplay" class="font-medium"></span></p>
                    </div>
                </div>

                <div class="space-y-4">
                    <button id="unsubscribeBtn" class="w-full bg-red-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-red-700 transition-colors">
                        取消订阅
                    </button>
                    
                    <button id="logoutBtn" class="w-full bg-gray-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-gray-700 transition-colors">
                        退出登录
                    </button>
                </div>
            </div>

            <!-- Info Section -->
            <div class="mt-8 border-t pt-6">
                <h3 class="text-lg font-semibold text-gray-800 mb-3">💡 关于AI洞察日报</h3>
                <ul class="space-y-2 text-gray-700">
                    <li>✅ 每天精选15条AI行业动态（海外12条 + 国内3条）</li>
                    <li>✅ 五大板块：大模型、Agent产品、产业动态、国内动态、开发者工具</li>
                    <li>✅ 深度聚焦：每板块附带专业分析与趋势洞察</li>
                    <li>✅ 林克自述：AI助手的自我进化感悟</li>
                </ul>
            </div>

            <!-- Footer -->
            <div class="mt-8 text-center text-gray-500 text-sm">
                <p>Powered by 林克（沈浪的AI分身）</p>
                <p class="mt-1">
                    <a href="https://xiaoxiong20260206.github.io/ai-insight/" class="text-blue-600 hover:underline">查看往期日报</a>
                </p>
            </div>
        </div>
    </div>

    <!-- Toast Notification -->
    <div id="toast" class="fixed top-4 right-4 bg-white rounded-lg shadow-lg p-4 max-w-sm transform translate-x-full transition-transform duration-300">
        <div class="flex items-center">
            <span id="toastIcon" class="text-2xl mr-3"></span>
            <p id="toastMessage" class="text-gray-800"></p>
        </div>
    </div>

    <script type="module">
        import { Client, Account, Databases, Query, OAuthProvider } from 'https://cdn.jsdelivr.net/npm/@cf/appwrite@latest/dist/module/index.js';

        // Appwrite Configuration
        const client = new Client()
            .setEndpoint('https://INTERNAL_SERVICE_ENDPOINT/v1')
            .setProject('INTERNAL_PROJECT_ID');

        const account = new Account(client);
        const db = new Databases(client);

        const DATABASE_ID = 'INTERNAL_DATABASE_ID';
        const COLLECTION_ID = 'INTERNAL_COLLECTION_ID';

        // Elements
        const loginSection = document.getElementById('loginSection');
        const subscriptionSection = document.getElementById('subscriptionSection');
        const loginBtn = document.getElementById('loginBtn');
        const unsubscribeBtn = document.getElementById('unsubscribeBtn');
        const logoutBtn = document.getElementById('logoutBtn');
        const usernameDisplay = document.getElementById('usernameDisplay');
        const subscribedAtDisplay = document.getElementById('subscribedAtDisplay');
        const statusBadge = document.getElementById('statusBadge');

        // Check if returning from OAuth
        async function handleOAuthCallback() {
            try {
                // Handle token exchange
                const urlParams = new URLSearchParams(window.location.search);
                const secret = urlParams.get('secret');
                const userId = urlParams.get('userId');

                if (secret && userId) {
                    await account.createSession(userId, secret);
                    // Clean URL
                    window.history.replaceState({}, document.title, window.location.pathname);
                }
            } catch (error) {
                console.error('OAuth callback error:', error);
            }
        }

        // Check current session
        async function checkSession() {
            try {
                const user = await account.get();
                showSubscriptionSection(user);
            } catch (error) {
                showLoginSection();
            }
        }

        // Show login section
        function showLoginSection() {
            loginSection.classList.remove('hidden');
            subscriptionSection.classList.add('hidden');
        }

        // Show subscription section
        async function showSubscriptionSection(user) {
            loginSection.classList.add('hidden');
            subscriptionSection.classList.remove('hidden');

            // Get subscription status
            try {
                const result = await db.listRows(
                    DATABASE_ID,
                    COLLECTION_ID,
                    [
                        Query.equal('username', user.name),
                        Query.limit(1)
                    ]
                );

                const rows = result.rows || [];
                
                if (rows.length > 0) {
                    const sub = rows[0];
                    usernameDisplay.textContent = user.name;
                    subscribedAtDisplay.textContent = new Date(sub.subscribed_at).toLocaleDateString('zh-CN');
                    
                    if (!sub.is_active) {
                        statusBadge.textContent = '已取消';
                        statusBadge.className = 'px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800';
                        unsubscribeBtn.textContent = '重新订阅';
                        unsubscribeBtn.className = 'w-full bg-green-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-green-700 transition-colors';
                    }
                } else {
                    // Auto subscribe on first login
                    await subscribe(user);
                }
            } catch (error) {
                console.error('Error fetching subscription:', error);
                showToast('❌', '获取订阅状态失败');
            }
        }

        // Login with Kuaishou SSO
        loginBtn.addEventListener('click', async () => {
            try {
                await account.createOAuth2Session(
                    OAuthProvider.Internal,
                    window.location.origin + '/subscription.html',
                    window.location.origin + '/subscription.html'
                );
            } catch (error) {
                showToast('❌', '登录失败：' + error.message);
            }
        });

        // Unsubscribe
        unsubscribeBtn.addEventListener('click', async () => {
            try {
                const user = await account.get();
                const result = await db.listRows(
                    DATABASE_ID,
                    COLLECTION_ID,
                    [Query.equal('username', user.name), Query.limit(1)]
                );

                if (result.rows.length > 0) {
                    const sub = result.rows[0];
                    const isActive = sub.is_active;
                    
                    await db.updateRow(
                        DATABASE_ID,
                        COLLECTION_ID,
                        sub.$id,
                        { is_active: !isActive }
                    );

                    if (isActive) {
                        showToast('✅', '已取消订阅');
                        statusBadge.textContent = '已取消';
                        statusBadge.className = 'px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800';
                        unsubscribeBtn.textContent = '重新订阅';
                        unsubscribeBtn.className = 'w-full bg-green-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-green-700 transition-colors';
                    } else {
                        showToast('✅', '订阅成功');
                        statusBadge.textContent = '已订阅';
                        statusBadge.className = 'px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800';
                        unsubscribeBtn.textContent = '取消订阅';
                        unsubscribeBtn.className = 'w-full bg-red-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-red-700 transition-colors';
                    }
                }
            } catch (error) {
                showToast('❌', '操作失败：' + error.message);
            }
        });

        // Logout
        logoutBtn.addEventListener('click', async () => {
            try {
                await account.deleteSession('current');
                showLoginSection();
                showToast('✅', '已退出登录');
            } catch (error) {
                showToast('❌', '退出失败');
            }
        });

        // Subscribe helper
        async function subscribe(user) {
            try {
                await db.createRow(
                    DATABASE_ID,
                    COLLECTION_ID,
                    'unique()',
                    {
                        username: user.name,
                        employee_name: user.name,
                        subscribed_at: new Date().toISOString(),
                        is_active: true,
                        preferences: '{}'
                    }
                );
                
                usernameDisplay.textContent = user.name;
                subscribedAtDisplay.textContent = new Date().toLocaleDateString('zh-CN');
                showToast('✅', '订阅成功！每天09:00会收到林克推送的AI日报');
            } catch (error) {
                console.error('Subscribe error:', error);
            }
        }

        // Toast notification
        function showToast(icon, message) {
            const toast = document.getElementById('toast');
            const toastIcon = document.getElementById('toastIcon');
            const toastMessage = document.getElementById('toastMessage');

            toastIcon.textContent = icon;
            toastMessage.textContent = message;

            toast.classList.remove('translate-x-full');

            setTimeout(() => {
                toast.classList.add('translate-x-full');
            }, 3000);
        }

        // Initialize
        handleOAuthCallback();
        checkSession();
    </script>
</body>
</html>
