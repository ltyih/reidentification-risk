import argparse
import csv
from collections import Counter
from pathlib import Path
from itertools import combinations

import numpy as np
from scipy.special import hyp2f1

# 复制 BF 风险计算函数
def bf_risk(f_k, p_hat):
    """Benedetti-Franconi individual disclosure risk"""
    if not (isinstance(f_k, (int, float, np.integer)) and f_k == int(f_k) and f_k > 0):
        raise ValueError(f"f_k must be a positive integer, got {f_k}")
    if not (0 < p_hat <= 1):
        raise ValueError(f"p_hat must be in (0, 1], got {p_hat}")
    
    if p_hat == 1.0:
        return 1.0 / f_k

    if f_k > 40:
        denominator = f_k - (1.0 - p_hat)
        if denominator <= 0:
            return 1.0
        r = p_hat / denominator
        return min(r, 1.0)

    q = 1 - p_hat
    r = (p_hat ** f_k) / f_k * hyp2f1(f_k, f_k, f_k + 1, q)
    return min(r, 1.0)


def calculate_p_hat(f_k, weights_k):
    """Calculate p_hat = f_k / sum(weights_k)"""
    if f_k <= 0:
        raise ValueError(f"f_k must be positive, got {f_k}")
    
    total_weight = np.sum(weights_k)
    if total_weight <= 0:
        raise ValueError("sum of weights_k must be positive")
    
    p_hat = f_k / total_weight
    
    if p_hat > 1.0:
        p_hat = 1.0
    if p_hat <= 0:
        p_hat = 1e-10
    
    return p_hat


def load_csv(path: Path) -> list[dict]:
    """Load CSV file with automatic encoding detection"""
    for encoding in ("utf-8", "cp936"):
        try:
            with path.open(newline="", encoding=encoding) as f:
                reader = csv.DictReader(f)
                return [row for row in reader]
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Unable to read CSV file: {path}")


def get_all_combinations(rows: list[dict], columns: list[str], weight_col: str) -> list[dict]:
    """
    找出所有唯一的列组合，并计算每个组合的：
    - 频数 (f_k)
    - 总权重和
    - p_hat
    - BF 风险值
    """
    # 按组合分组
    group_data = {}
    
    for row in rows:
        # 构建组合键
        key = tuple(row[col] for col in columns)
        
        # 获取权重
        try:
            weight = float(row[weight_col])
        except (ValueError, TypeError):
            continue
        
        if key not in group_data:
            group_data[key] = {
                'count': 0,
                'weights': []
            }
        
        group_data[key]['count'] += 1
        group_data[key]['weights'].append(weight)
    
    # 计算每个组合的风险
    results = []
    for key, data in group_data.items():
        f_k = data['count']
        weights_k = data['weights']
        
        try:
            p_hat = calculate_p_hat(f_k, weights_k)
            risk = bf_risk(f_k, p_hat)
            
            # 构建结果行
            result_row = {}
            for i, col in enumerate(columns):
                result_row[col] = key[i]
            
            result_row['f_k'] = f_k
            result_row['total_weight'] = sum(weights_k)
            result_row['p_hat'] = p_hat
            result_row['bf_risk'] = risk
            
            results.append(result_row)
        except Exception as e:
            print(f"Warning: Could not calculate risk for {key}: {e}")
            continue
    
    return results


def write_results(results: list[dict], output_path: Path, columns: list[str]) -> None:
    """Write results to CSV file"""
    if not results:
        print("No results to write")
        return
    
    fieldnames = columns + ['f_k', 'total_weight', 'p_hat', 'bf_risk']
    
    with output_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # 按风险值降序排序（高风险优先）
        sorted_results = sorted(results, key=lambda x: x['bf_risk'], reverse=True)
        writer.writerows(sorted_results)
    
    print(f"Results written to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Calculate BF disclosure risk for all combinations of specified columns"
    )
    parser.add_argument("--csv", dest="csv_path", required=True, help="Path to CSV file")
    parser.add_argument(
        "--columns",
        required=True,
        help="Comma-separated list of columns to analyze (e.g., 'region,age,sex')"
    )
    parser.add_argument(
        "--weight-column",
        default="weight",
        help="Name of the weight column (default: 'weight')"
    )
    parser.add_argument(
        "--output",
        default="risk_analysis.csv",
        help="Output CSV file path (default: 'risk_analysis.csv')"
    )
    parser.add_argument(
        "--min-count",
        type=int,
        default=1,
        help="Minimum frequency to include (default: 1)"
    )
    parser.add_argument(
        "--max-risk",
        type=float,
        help="Only output combinations with risk > this value"
    )
    
    args = parser.parse_args()
    
    csv_path = Path(args.csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    print(f"Loading CSV: {csv_path}")
    rows = load_csv(csv_path)
    print(f"Loaded {len(rows)} rows")
    
    columns = [col.strip() for col in args.columns.split(",") if col.strip()]
    if not columns:
        raise ValueError("At least one column is required")
    
    # 检查列是否存在
    sample_row = rows[0]
    missing_cols = [col for col in columns if col not in sample_row]
    if missing_cols:
        raise ValueError(f"Columns not found in CSV: {missing_cols}")
    
    if args.weight_column not in sample_row:
        raise ValueError(f"Weight column '{args.weight_column}' not found in CSV")
    
    print(f"Analyzing combinations of: {columns}")
    print(f"Weight column: {args.weight_column}")
    
    # 计算所有组合的风险
    results = get_all_combinations(rows, columns, args.weight_column)
    
    # 过滤结果
    filtered_results = [r for r in results if r['f_k'] >= args.min_count]
    
    if args.max_risk is not None:
        filtered_results = [r for r in filtered_results if r['bf_risk'] > args.max_risk]
    
    print(f"Found {len(results)} unique combinations")
    print(f"After filtering: {len(filtered_results)} combinations")
    
    if filtered_results:
        # 显示风险最高的前10个
        sorted_by_risk = sorted(filtered_results, key=lambda x: x['bf_risk'], reverse=True)
        print("\nTop 10 highest risk combinations:")
        print("-" * 80)
        for i, result in enumerate(sorted_by_risk[:10], 1):
            combo = ", ".join(f"{col}={result[col]}" for col in columns)
            print(f"{i}. {combo}")
            print(f"   f_k={result['f_k']}, p_hat={result['p_hat']:.6f}, risk={result['bf_risk']:.6f}")
    
    # 写入结果
    write_results(filtered_results, Path(args.output), columns)
    
    # 统计摘要
    if filtered_results:
        risks = [r['bf_risk'] for r in filtered_results]
        print(f"\nSummary:")
        print(f"  Total combinations: {len(filtered_results)}")
        print(f"  Risk range: {min(risks):.6f} - {max(risks):.6f}")
        print(f"  Mean risk: {np.mean(risks):.6f}")
        print(f"  Median risk: {np.median(risks):.6f}")
        
        high_risk = [r for r in filtered_results if r['bf_risk'] > 0.1]
        if high_risk:
            print(f"  High risk (>0.1): {len(high_risk)} combinations")
            for r in high_risk[:5]:
                combo = ", ".join(f"{col}={r[col]}" for col in columns)
                print(f"    - {combo}: risk={r['bf_risk']:.6f}")


if __name__ == "__main__":
    main()