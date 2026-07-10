export const config = { runtime: 'nodejs' };

   export default async function handler(req, res) {
     if (req.method !== 'POST') return res.status(405).end();

     const { filename, content } = req.body;
     const REPO = process.env.REPO;
     const TOKEN = process.env.GH_TOKEN;

     const path = `ipa/${filename}`;
     const url = `https://api.github.com/repos/${REPO}/contents/${path}`;

     const r = await fetch(url, {
       method: 'PUT',
       headers: {
         Authorization: `Bearer ${TOKEN}`,
         Accept: 'application/vnd.github+json',
       },
       body: JSON.stringify({
         message: `upload ${filename}`,
         content: content,
       }),
     });

     if (r.ok) return res.status(200).json({ ok: true });
     const err = await r.text();
     return res.status(500).json({ ok: false, err });
   }
