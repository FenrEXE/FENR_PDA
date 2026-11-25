/*
    Fenrir Industries PDA
    Copyright: Fenr.EXE
    Maintainer: Fenr.EXE

    Helpers shared by the trade and bounty boards (v8.8).
*/

class FENR_PDA_Board
{
    protected static int s_Counter = 0;

    // Trims, flattens to one line and caps the length.
    static string CleanText(string text, int maxChars)
    {
        string result = text;
        result.Replace("\n", " ");
        result.Replace("\r", " ");
        result = result.Trim();
        if (result.LengthUtf8() > maxChars)
            result = result.SubstringUtf8(0, maxChars);
        return result;
    }

    // Unique listing / bounty ID ("T..." / "B...").
    static string NewID(string prefix)
    {
        s_Counter++;
        int now = GetGame().GetTime();
        int salt = Math.RandomInt(1000, 9999);
        return prefix + now.ToString() + "_" + s_Counter.ToString() + "_" + salt.ToString();
    }

    // Clamps `page` to the results and returns the slice [start, end).
    static void PageSlice(int total, int page, int pageSize, out int pageOut, out int start, out int end)
    {
        int maxPage = 0;
        if (total > 0)
            maxPage = (total - 1) / pageSize;
        if (page > maxPage)
            page = maxPage;
        if (page < 0)
            page = 0;
        pageOut = page;
        start = page * pageSize;
        end = start + pageSize;
        if (end > total)
            end = total;
    }

    // "MM-DD HH:MM" from a storage timestamp.
    static string Posted(string created)
    {
        if (created.Length() >= 16)
            return created.Substring(5, 11);
        return created;
    }
};
