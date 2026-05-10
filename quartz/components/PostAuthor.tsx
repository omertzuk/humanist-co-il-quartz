import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"
import { classNames } from "../util/lang"
import { joinSegments, pathToRoot } from "../util/path"

function getAuthorLogin(authorField: unknown): string | null {
  if (typeof authorField === "string") {
    const wikilinkMatch = authorField.match(/^\[\[(.+?)\]\]$/)
    return (wikilinkMatch?.[1] ?? authorField).trim() || null
  }

  if (Array.isArray(authorField) && authorField.length > 0) {
    return getAuthorLogin(authorField[0])
  }

  if (authorField && typeof authorField === "object") {
    const maybeValue = (authorField as { value?: unknown; path?: unknown; slug?: unknown }).value ??
      (authorField as { value?: unknown; path?: unknown; slug?: unknown }).path ??
      (authorField as { value?: unknown; path?: unknown; slug?: unknown }).slug
    if (typeof maybeValue === "string") {
      return maybeValue.trim() || null
    }
  }

  return null
}

function resolveAuthorName(authorLogin: string | null, allFiles: QuartzComponentProps["allFiles"]): string | null {
  if (!authorLogin) {
    return null
  }

  const authorSlug = `כותבים/${authorLogin}`
  const authorFile = allFiles.find((file) => file.slug === authorSlug || file.slug === authorLogin)
  return authorFile?.frontmatter?.title ?? authorLogin
}

const PostAuthor: QuartzComponent = ({ fileData, allFiles }: QuartzComponentProps) => {
  if (!fileData.slug?.startsWith("מאמרים/")) {
    return null
  }

  const authorLogin = getAuthorLogin(fileData.frontmatter?.author)
  const authorName = resolveAuthorName(authorLogin, allFiles)

  if (!authorName) {
    return null
  }

  const authorHref = authorLogin
    ? joinSegments(pathToRoot(fileData.slug!), "כותבים", authorLogin)
    : undefined

  return (
    <p class={classNames("post-author")}>
      {authorHref ? <a href={authorHref}>{authorName}</a> : authorName}
    </p>
  )
}

PostAuthor.css = `
.post-author {
  margin: 0.35rem 0 0.15rem 0;
  color: var(--darkgray);
  font-size: 0.95rem;
  font-weight: 500;
}

.post-author a {
  color: inherit;
  text-decoration: none;
}

.post-author a:hover {
  text-decoration: underline;
}
`

export default (() => PostAuthor) satisfies QuartzComponentConstructor