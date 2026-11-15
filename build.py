<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>__TITLE__</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #047857; /* Vert HSE / Sécurité */
            --primary-light: #ecfdf5;
            --secondary: #0284c7; /* Bleu technique */
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --text-main: #0f172a;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --radius: 14px;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            line-height: 1.7;
            display: flex;
            min-height: 100vh;
        }

        /* Barre latérale moderne */
        sidebar {
            width: 300px;
            background: var(--card-bg);
            border-right: 1px solid var(--border);
            padding: 2rem 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 2rem;
            position: fixed;
            height: 100vh;
            overflow-y: auto;
            box-shadow: 4px 0 15px rgba(0, 0, 0, 0.02);
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .brand-badge {
            background: var(--primary-light);
            color: var(--primary);
            font-weight: 700;
            padding: 0.5rem 0.75rem;
            border-radius: 10px;
            font-size: 1.1rem;
        }

        .brand h1 {
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--text-main);
        }

        .brand span {
            font-size: 0.8rem;
            color: var(--text-muted);
        }

        .nav-section {
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
        }

        .nav-title {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--text-muted);
            font-weight: 700;
            margin-bottom: 0.25rem;
        }

        .nav-item {
            padding: 0.7rem 1rem;
            border-radius: 10px;
            color: var(--text-main);
            text-decoration: none;
            font-size: 0.95rem;
            font-weight: 600;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .nav-item:hover, .nav-item.active {
            background-color: var(--primary-light);
            color: var(--primary);
            transform: translateX(4px);
        }

        .sub-nav {
            padding-left: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 0.2rem;
            margin-top: 0.2rem;
            border-left: 2px solid var(--border);
            margin-left: 1rem;
        }

        .sub-nav a {
            font-size: 0.88rem;
            padding: 0.4rem 0.75rem;
            color: var(--text-muted);
            text-decoration: none;
            border-radius: 6px;
            transition: all 0.2s ease;
        }

        .sub-nav a:hover {
            color: var(--primary);
            background-color: var(--primary-light);
        }

        /* Contenu principal fluide */
        main {
            margin-left: 300px;
            flex: 1;
            padding: 3rem;
            max-width: 1100px;
        }

        .header-banner {
            background: linear-gradient(135deg, #065f46, #047857);
            color: white;
            padding: 2.5rem;
            border-radius: var(--radius);
            margin-bottom: 2.5rem;
            box-shadow: 0 10px 25px -5px rgba(4, 120, 87, 0.2);
        }

        .header-banner h2 {
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }

        .header-banner p {
            opacity: 0.9;
            font-size: 1.05rem;
        }

        .content-card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 3rem;
            box-shadow: var(--shadow);
        }

        /* Styles dynamiques injectés par le script */
        __DOCCSS__

        @media (max-width: 768px) {
            sidebar {
                display: none;
            }
            main {
                margin-left: 0;
                padding: 1.5rem;
            }
        }
    </style>
</head>
<body>

    <!-- Barre latérale de navigation -->
    <sidebar>
        <div class="brand">
            <div class="brand-badge">S3</div>
            <div>
                <h1>HSE 2</h1>
                <span>Plateforme Pédagogique</span>
            </div>
        </div>

        <div class="nav-section">
            <span class="nav-title">Modules / Profs</span>
            <a href="#" class="nav-item active">👨‍🏫 Albert</a>
            <div class="sub-nav">
                <a href="#ergonomie">Ergonomie</a>
            </div>
        </div>

        <div class="nav-section">
            <span class="nav-title">Projets & Travaux</span>
            <a href="#" class="nav-item">🛠️ SAE</a>
            <div class="sub-nav">
                <a href="#sae301">SAE 3.01</a>
                <a href="#sae302">SAE 3.02</a>
            </div>
            <a href="#" class="nav-item">🇪🇸 Stage Espagne</a>
        </div>
