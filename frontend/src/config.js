const dev = {
  url: "http://localhost:8080"
}

const prod = {
  url: "https://udebs.ak-rc.net"
}

export const config = process.env.REACT_APP_ENV === "prod"
  ? prod
  : dev;