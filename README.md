# -<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SPINX - 디지털 음반 이력서</title>
    <style>
        :root {
            --primary: #2563eb;
            --dark: #1e293b;
            --gold: #fbbf24;
            --gray: #f1f5f9;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: var(--gray);
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
        }
        .container {
            max-width: 400px;
            width: 100%;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background-color: var(--dark);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .header h1 { margin: 0; font-size: 24px; letter-spacing: 2px; }
        .badge {
            display: inline-block;
            background: var(--gold);
            color: black;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin-top: 10px;
        }
        .album-info {
            padding: 20px;
            text-align: center;
        }
        .album-art {
            width: 200px;
            height: 200px;
            background: #ddd;
            margin: 0 auto 15px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 50px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }
        .section-title {
            font-size: 16px;
            font-weight: bold;
            color: var(--dark);
            border-left: 4px solid var(--primary);
            padding-left: 10px;
            margin: 20px 0 10px;
        }
        .data-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            padding: 0 20px;
        }
        .data-item {
            background: #f8fafc;
            padding: 10px;
            border-radius: 10px;
            font-size: 13px;
        }
        .data-label { color: #64748b; display: block; margin-bottom: 4px; }
        .data-value { font-weight: bold; color: var(--dark); }
        
        .graph-container {
            padding: 0 20px 20px;
        }
        .graph-bar {
            height: 12px;
            background: #e2e8f0;
            border-radius: 6px;
            margin-bottom: 15px;
            position: relative;
        }
        .graph-fill {
            height: 100%;
            background: var(--primary);
            border-radius: 6px;
            transition: width 1s ease-in-out;
        }
        .footer {
            text-align: center;
            padding: 20px;
            font-size: 12px;
            color: #94a3b8;
            border-top: 1px dashed #e2e8f0;
        }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <h1>SPINX</h1>
        <div class="badge">CERTIFIED RECOVERY</div>
    </div>

    <div class="album-info">
        <div class="album-art">💿</div>
        <h2 id="album-title" style="margin:5px 0;">유재하 1집</h2>
        <p style="color:#64748b; margin:0;">사랑하기 때문에</p>
    </div>

    <div class="section-title" style="margin-left:20px;">Restoration History</div>
    <div class="data-grid">
        <div class="data-item">
            <span class="data-label">복원 날짜</span>
            <span class="data-value">2026.02.17</span>
        </div>
        <div class="data-item">
            <span class="data-label">복원 방식</span>
            <span class="data-value">Ultrasonic + UV</span>
        </div>
        <div class="data-item">
            <span class="data-label">담당 검수자</span>
            <span class="data-value">도윤 (Lead)</span>
        </div>
        <div class="data-item">
            <span class="data-label">시리얼 번호</span>
            <span class="data-value">SPX-001-2026</span>
        </div>
    </div>

    <div class="section-title" style="margin-left:20px;">Quality Improvement</div>
    <div class="graph-container">
        <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:5px;">
            <span>음질 선명도 (Before → After)</span>
            <span style="color:var(--primary); font-weight:bold;">+35% 향상</span>
        </div>
        <div class="graph-bar">
            <div class="graph-fill" style="width: 85%;"></div>
        </div>
        
        <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:5px;">
            <span>노이즈 제거율</span>
            <span style="color:var(--primary); font-weight:bold;">92% 완료</span>
        </div>
        <div class="graph-bar">
            <div class="graph-fill" style="width: 92%;"></div>
        </div>
    </div>

    <div class="footer">
        SPINX Analog Record Tech Lab<br>
        강원특별자치도 강릉시 (가톨릭관동대학교)
    </div>
</div>

</body>
</html>
spinx
