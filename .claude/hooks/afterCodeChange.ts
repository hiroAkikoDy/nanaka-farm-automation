/**
 * After Code Change Hook
 * .cypherファイルの変更を検知してCypher構文チェックを実行
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import * as path from 'path';

const execAsync = promisify(exec);

interface AfterCodeChangeParams {
  filePath: string;
  operation: 'create' | 'edit' | 'delete';
}

export default async function afterCodeChange(params: AfterCodeChangeParams) {
  const { filePath, operation } = params;

  // .cypherファイルの変更のみ処理
  if (!filePath.endsWith('.cypher')) {
    return;
  }

  // ファイル削除時は何もしない
  if (operation === 'delete') {
    return;
  }

  console.log(`\n🔍 Cypher構文チェック: ${path.basename(filePath)}`);

  try {
    // cypher-shellの存在確認
    try {
      await execAsync('cypher-shell --version');
    } catch (versionError) {
      console.log('⚠️  cypher-shellが見つかりません。構文チェックをスキップします。');
      console.log('   Neo4jをインストールするか、PATHにcypher-shellを追加してください。');
      return;
    }

    // Cypherファイルの構文チェック
    // Note: cypher-shellは実際の接続なしでは構文チェックできないため、
    // 代替として基本的な構文パターンのチェックを行う
    const { readFile } = await import('fs/promises');
    const content = await readFile(filePath, 'utf-8');

    // 基本的な構文チェック
    const issues: string[] = [];

    // 空のクエリチェック
    if (content.trim().length === 0) {
      issues.push('ファイルが空です');
    }

    // 基本的なCypherキーワードの存在チェック
    const cypherKeywords = /\b(MATCH|CREATE|MERGE|RETURN|WHERE|WITH|DELETE|SET|REMOVE)\b/i;
    if (content.trim().length > 0 && !cypherKeywords.test(content)) {
      issues.push('有効なCypherキーワードが見つかりません');
    }

    // セミコロンで複数のステートメントに分割
    const statements = content.split(';').filter(s => s.trim().length > 0);

    // 各ステートメントの基本チェック
    for (let i = 0; i < statements.length; i++) {
      const stmt = statements[i].trim();

      // 括弧のバランスチェック
      const openParens = (stmt.match(/\(/g) || []).length;
      const closeParens = (stmt.match(/\)/g) || []).length;
      if (openParens !== closeParens) {
        issues.push(`ステートメント ${i + 1}: 括弧 () の数が一致しません`);
      }

      const openBrackets = (stmt.match(/\[/g) || []).length;
      const closeBrackets = (stmt.match(/\]/g) || []).length;
      if (openBrackets !== closeBrackets) {
        issues.push(`ステートメント ${i + 1}: 角括弧 [] の数が一致しません`);
      }

      const openBraces = (stmt.match(/\{/g) || []).length;
      const closeBraces = (stmt.match(/\}/g) || []).length;
      if (openBraces !== closeBraces) {
        issues.push(`ステートメント ${i + 1}: 波括弧 {} の数が一致しません`);
      }
    }

    if (issues.length > 0) {
      console.log('❌ 構文エラーが検出されました:\n');
      issues.forEach(issue => {
        console.log(`   • ${issue}`);
      });
      console.log('\n💡 修正提案:');
      console.log('   - 括弧、角括弧、波括弧のペアが正しく閉じられているか確認してください');
      console.log('   - 有効なCypherキーワード (MATCH, CREATE, RETURN等) を使用してください');
      console.log('   - セミコロン (;) でステートメントを区切ってください');
    } else {
      console.log('✅ 基本的な構文チェック: OK');
      console.log(`   ${statements.length} 個のステートメントが見つかりました`);
    }

  } catch (error) {
    console.error('❌ 構文チェック中にエラーが発生しました:', error);
  }
}
