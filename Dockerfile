# Node 이미지
FROM node:23.6-alpine

# 디렉터리 설정
WORKDIR /app

# package.json 복사
COPY package*.json ./

# npm 패키지 설치 (production)
RUN npm ci --only=production

# 코드 복사
COPY . .

# 환경 변수 설정
ENV NODE_ENV=production
ENV PORT=8000

# 실행 명령어
CMD ["node", "server.js"]

# 포트
EXPOSE 8000

# HEALTHCHECK
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD nc -z localhost 8000 || exit 1